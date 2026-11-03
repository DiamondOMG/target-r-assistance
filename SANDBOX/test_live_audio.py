from __future__ import annotations

import argparse
import asyncio
import base64
import wave
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from google import genai

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "gemini-3.1-flash-live-preview"
OUTPUT_SAMPLE_RATE = 24_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a Gemini Live session, request a spoken reply, and save it as WAV."
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini Live model name")
    parser.add_argument(
        "--prompt",
        default="สวัสดี ช่วยพูดแนะนำตัวสั้น ๆ เป็นภาษาไทย",
        help="Text prompt sent to the Live session",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("response.wav"),
        help="Output WAV path (default: SANDBOX/response.wav)",
    )
    return parser.parse_args()


def load_api_key() -> str:
    env_file = PROJECT_ROOT / ".env"
    api_key = dotenv_values(env_file).get("GEMINI_API_VOICE")
    if not api_key:
        raise RuntimeError(
            f"GEMINI_API_VOICE is missing or empty in {env_file}. "
            "Set it locally; do not paste the key into source code."
        )
    return api_key


def get_audio_bytes(part: Any) -> bytes | None:
    inline_data = getattr(part, "inline_data", None)
    data = getattr(inline_data, "data", None)
    if isinstance(data, str):
        return base64.b64decode(data)
    if isinstance(data, bytes):
        return data
    return None


async def run_test(args: argparse.Namespace) -> None:
    client = genai.Client(
        api_key=load_api_key(),
        http_options={"api_version": "v1beta"},
    )
    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": (
            "ตอบเป็นภาษาไทยอย่างเป็นธรรมชาติ กระชับ และสร้างคำตอบเป็นเสียงพูด"
        ),
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {"voice_name": "Puck"}
            }
        },
        "output_audio_transcription": {},
    }

    audio_chunks: list[bytes] = []
    transcript: list[str] = []
    turn_completed = False

    async with client.aio.live.connect(model=args.model, config=config) as session:
        print(f"Connected to Gemini Live model: {args.model}")
        await session.send_client_content(
            turns={"role": "user", "parts": [{"text": args.prompt}]},
            turn_complete=True,
        )

        async with asyncio.timeout(60):
            async for response in session.receive():
                server_content = response.server_content
                if server_content is None:
                    continue

                output_transcription = server_content.output_transcription
                if output_transcription and output_transcription.text:
                    transcript.append(output_transcription.text)

                model_turn = server_content.model_turn
                if model_turn:
                    for part in model_turn.parts:
                        audio_data = get_audio_bytes(part)
                        if audio_data:
                            audio_chunks.append(audio_data)

                if server_content.turn_complete:
                    turn_completed = True
                    break

    if not audio_chunks:
        raise RuntimeError(
            "The Live session completed without returning audio. "
            "Check the model name, API access, and quota."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(args.output), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(OUTPUT_SAMPLE_RATE)
        wav_file.writeframes(b"".join(audio_chunks))

    print(f"Turn completed: {turn_completed}")
    if transcript:
        print("Transcript:", "".join(transcript).strip())
    print(f"Received {len(audio_chunks)} audio chunks")
    print(f"Saved WAV: {args.output.resolve()}")


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run_test(args))
    except TimeoutError:
        raise SystemExit("Timed out waiting for the Live API response.") from None
    except KeyboardInterrupt:
        raise SystemExit("Test cancelled.") from None


if __name__ == "__main__":
    main()
