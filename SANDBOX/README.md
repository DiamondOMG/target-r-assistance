# Gemini Live API Sandbox

Small server-side smoke test for `gemini-3.1-flash-live-preview` (default). It sends a text prompt to a Live API session and saves the spoken response as `response.wav`. No browser or microphone is required for this API/audio-output test.

## Setup (Git Bash, from the repository root)

```bash
python -m venv SANDBOX/.venv
source SANDBOX/.venv/Scripts/activate
python -m pip install -r SANDBOX/requirements.txt
```

The script reads `GEMINI_API_VOICE` from the repository-root `.env`. Keep the key out of source files and chat; do not commit `.env`.

## Run

```bash
python SANDBOX/test_live_audio.py
```

Optional arguments:

```bash
python SANDBOX/test_live_audio.py --prompt "ช่วยพูดทักทายเป็นภาษาไทย" --output SANDBOX/response.wav
python SANDBOX/test_live_audio.py --model gemini-2.5-flash-native-audio-latest
```

A successful run reports the selected model, any returned transcript, the number of audio chunks, and the WAV output path. The WAV is mono 16-bit PCM at 24 kHz. This only tests text-to-audio over a Live session; microphone streaming/input transcription can be added as the next sandbox test.

## Test the Target-R Skill and tool calling

```bash
python SANDBOX/test_skill_tool.py
```

This loads `SKILLS/targetr_system.md` and the `targetr_query` contract, starts the real MCP server over stdio, discovers its tool schema, and calls `targetr_query` for a cached Screen count. It does not request `freshness=refresh`, so it does not trigger Target-R sync/upsert. No microphone is used. The sandbox environment needs `google-genai`, `mcp`, and `python-dotenv`; the MCP server must also have its own `.venv` and the root `.env` must define `GEMINI_API_VOICE`, `NEON_FUNCTION_URL`, and `NEON_MANUAL_SYNC_TOKEN`.
