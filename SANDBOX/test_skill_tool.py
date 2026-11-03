from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import wave
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_DIR = Path(__file__).resolve().parent
MCP_DIR = PROJECT_ROOT / "MCP_SERVER"
MCP_PYTHON = MCP_DIR / ".venv" / "Scripts" / "python.exe"
DEFAULT_MODEL = "gemini-3.1-flash-live-preview"
OUTPUT_SAMPLE_RATE = 24_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test Gemini Live with the real Target-R MCP server over stdio."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini Live model name")
    parser.add_argument(
        "--question",
        default="ในข้อมูลที่เชื่อมอยู่มี Screen ทั้งหมดกี่จอ?",
        help="Question to ask using the Target-R Skill",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SANDBOX_DIR / "skill_tool_response.wav",
        help="Where to save the model's spoken response",
    )
    return parser.parse_args()


def load_env() -> dict[str, str]:
    values = dotenv_values(PROJECT_ROOT / ".env")
    env = os.environ.copy()
    for name in ("GEMINI_API_VOICE", "NEON_FUNCTION_URL", "NEON_MANUAL_SYNC_TOKEN"):
        value = values.get(name) or env.get(name)
        if value:
            env[name] = value
    missing = [
        name
        for name in ("GEMINI_API_VOICE", "NEON_FUNCTION_URL", "NEON_MANUAL_SYNC_TOKEN")
        if not env.get(name)
    ]
    if missing:
        raise RuntimeError(f"Required environment settings are missing: {', '.join(missing)}")
    if not MCP_PYTHON.is_file():
        raise RuntimeError(f"MCP server virtualenv not found: {MCP_PYTHON}")
    return env


def load_prompt_context() -> str:
    skill = (PROJECT_ROOT / "SKILLS" / "targetr_system.md").read_text(encoding="utf-8")
    contract = (MCP_DIR / "TOOLS" / "targetr_query.md").read_text(encoding="utf-8")
    return (
        "You are Jarvis. Follow this Skill exactly:\n\n"
        f"{skill}\n\n"
        "Tool contract:\n\n"
        f"{contract}\n\n"
        "Use only the connected targetr_query tool for Target-R data. For this test, "
        "answer the user's count question using one count operation with freshness='cached'. "
        "Never request refresh or expose screen/device identifiers. After the tool "
        "returns, you MUST use its result to give the user a concise spoken answer "
        "in Thai; state the Screen count explicitly and clarify that it came from "
        "cached data. Do not end the interaction with only a tool call or tool result."
    )


def get_audio_bytes(part: Any) -> bytes | None:
    inline_data = getattr(part, "inline_data", None)
    data = getattr(inline_data, "data", None)
    if isinstance(data, str):
        return base64.b64decode(data)
    if isinstance(data, bytes):
        return data
    return None


def to_genai_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert JSON Schema types exposed by MCP to Gemini function declaration schema."""
    type_map = {
        "object": "OBJECT",
        "array": "ARRAY",
        "string": "STRING",
        "integer": "INTEGER",
        "number": "NUMBER",
        "boolean": "BOOLEAN",
    }
    result: dict[str, Any] = {}
    for key in ("type", "description", "enum", "required", "properties", "items"):
        if key not in schema:
            continue
        value = schema[key]
        if key == "type" and isinstance(value, str):
            result[key] = type_map.get(value.lower(), value.upper())
        elif key == "properties" and isinstance(value, dict):
            result[key] = {name: to_genai_schema(prop) for name, prop in value.items()}
        elif key == "items" and isinstance(value, dict):
            result[key] = to_genai_schema(value)
        else:
            result[key] = value
    return result


def get_mcp_text(result: Any) -> str:
    if getattr(result, "is_error", False):
        raise RuntimeError("MCP targetr_query returned an error")
    parts: list[str] = []
    for content in getattr(result, "content", []):
        text = getattr(content, "text", None)
        if text:
            parts.append(text)
    if not parts:
        return json.dumps({"status": "success"})
    return "\n".join(parts)


async def run_test(args: argparse.Namespace) -> None:
    env = load_env()
    client = genai.Client(
        api_key=env["GEMINI_API_VOICE"],
        http_options={"api_version": "v1beta"},
    )
    server_params = StdioServerParameters(
        command=str(MCP_PYTHON),
        args=["-m", "jarvis_mcp.server"],
        cwd=str(MCP_DIR),
        env=env,
    )
    tool_calls: list[dict[str, Any]] = []
    audio_chunks: list[bytes] = []
    transcripts: list[str] = []
    turn_completed = False
    tool_response_sent = False
    final_output_seen = False

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            await mcp_session.initialize()
            mcp_tools = await mcp_session.list_tools()
            targetr_tool = next(
                (tool for tool in mcp_tools.tools if tool.name == "targetr_query"),
                None,
            )
            if targetr_tool is None:
                raise RuntimeError("The MCP server did not expose targetr_query")

            tool_declaration = {
                "name": targetr_tool.name,
                "description": targetr_tool.description or "Query Target-R data.",
                "parameters": to_genai_schema(targetr_tool.inputSchema),
            }
            print("MCP connected over stdio; discovered targetr_query from server.")

            config = {
                "response_modalities": ["AUDIO"],
                "system_instruction": load_prompt_context(),
                "tools": [{"function_declarations": [tool_declaration]}],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {"voice_name": "Puck"}
                    }
                },
                "output_audio_transcription": {},
            }

            async with client.aio.live.connect(model=args.model, config=config) as session:
                print(f"Connected to Gemini Live model: {args.model}")
                await session.send_client_content(
                    turns={"role": "user", "parts": [{"text": args.question}]},
                    turn_complete=True,
                )

                async with asyncio.timeout(120):
                    async for response in session.receive():
                        response_data = getattr(response, "data", None)
                        if isinstance(response_data, bytes) and response_data:
                            audio_chunks.append(response_data)
                            final_output_seen = True

                        tool_call = response.tool_call
                        if tool_call and tool_call.function_calls:
                            function_responses: list[types.FunctionResponse] = []
                            for function_call in tool_call.function_calls:
                                name = function_call.name or ""
                                call_args = dict(function_call.args or {})
                                tool_calls.append({"name": name, "args": call_args})
                                print(
                                    "Calling MCP tool:",
                                    name,
                                    json.dumps(call_args, ensure_ascii=False),
                                )
                                if name != targetr_tool.name or not function_call.id:
                                    payload = {"error": "Unsupported or malformed tool call."}
                                else:
                                    mcp_result = await mcp_session.call_tool(
                                        name,
                                        arguments=call_args,
                                    )
                                    result_text = get_mcp_text(mcp_result)
                                    try:
                                        parsed_result = json.loads(result_text)
                                    except json.JSONDecodeError:
                                        parsed_result = None
                                    if isinstance(parsed_result, dict):
                                        print(
                                            "MCP result summary:",
                                            {
                                                "source": parsed_result.get("source"),
                                                "operation": parsed_result.get("operation"),
                                                "total": parsed_result.get("total"),
                                                "data_status": parsed_result.get("data_status"),
                                            },
                                        )
                                    payload = {
                                        "result": parsed_result if isinstance(parsed_result, dict) else result_text
                                    }
                                function_responses.append(
                                    types.FunctionResponse(
                                        id=function_call.id,
                                        name=name,
                                        response=payload,
                                    )
                                )
                            if function_responses:
                                await session.send_tool_response(
                                    function_responses=function_responses
                                )
                                tool_response_sent = True

                        server_content = response.server_content
                        if server_content is None:
                            continue

                        output_transcription = server_content.output_transcription
                        if output_transcription and output_transcription.text:
                            transcripts.append(output_transcription.text)
                            final_output_seen = True

                        model_turn = server_content.model_turn
                        if model_turn:
                            for part in model_turn.parts:
                                audio_data = get_audio_bytes(part)
                                if audio_data:
                                    audio_chunks.append(audio_data)
                                    final_output_seen = True

                        if server_content.turn_complete:
                            turn_completed = True
                            if tool_response_sent and not final_output_seen:
                                turn_completed = False
                                print("Tool turn ended; waiting for Gemini's final spoken answer...")
                                continue
                            break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if audio_chunks:
        with wave.open(str(args.output), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(OUTPUT_SAMPLE_RATE)
            wav_file.writeframes(b"".join(audio_chunks))

    print("MCP tool calls:")
    for index, call in enumerate(tool_calls, start=1):
        print(f"  {index}. {call['name']}: {json.dumps(call['args'], ensure_ascii=False)}")
    if transcripts:
        print("Assistant transcript:", "".join(transcripts).strip())
    if audio_chunks:
        print(f"Saved spoken response: {args.output.resolve()}")
    print(f"Turn completed: {turn_completed}")

    valid_tool_call = any(
        call["name"] == "targetr_query"
        and call["args"].get("entity") == "screen"
        and call["args"].get("operation") == "count"
        and call["args"].get("freshness", "cached") == "cached"
        for call in tool_calls
    )
    passed = valid_tool_call and turn_completed and bool(audio_chunks)
    print("Real MCP + Gemini Live test:", "PASS" if passed else "FAIL")
    if not passed:
        raise RuntimeError("Expected a cached Screen count via real MCP and a spoken answer.")


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run_test(args))
    except TimeoutError:
        raise SystemExit("Timed out waiting for the MCP or Gemini Live response.") from None
    except KeyboardInterrupt:
        raise SystemExit("Test cancelled.") from None


if __name__ == "__main__":
    main()
