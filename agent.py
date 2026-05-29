#!/usr/bin/env python3
"""
Free media generation agent — uses Gemini 2.0 Flash (orchestration),
FLUX.1-schnell via Hugging Face (images), minimax/video-01 via Replicate (video),
Edge TTS (speech), and MusicGen via Hugging Face (sound effects).

Usage:
    python agent.py --prompt "Create a video of a sunset with ambient waves"
"""

import argparse
import json
import os
import sys

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

import tools.image_tool as image_tool
import tools.video_tool as video_tool
import tools.audio_tool as audio_tool
import tools.combine_tool as combine_tool
from utils import is_dry_run

os.makedirs("output", exist_ok=True)

GEMINI_MODEL = "gemini-2.0-flash"

SYSTEM_PROMPT = """\
You are a media generation agent. Given a user's creative brief, you plan and \
execute the creation of media assets — images, video, and audio — by calling \
the available tools in the right sequence. When appropriate, combine video and \
audio into a final deliverable.

## Decision guide
- Pure image request → call generate_image once.
- Video request → call generate_video, then optionally generate_tts or \
generate_sound_effect for audio, then combine_video_audio.
- Narrated video → generate_video + generate_tts (speech) + optionally \
generate_sound_effect (ambient) + combine_video_audio.
- Audio-only request → generate_tts or generate_sound_effect.

## Prompting tips
- Expand the user's brief with vivid cinematic or artistic detail.
- For sound effects, describe the acoustic environment precisely \
(e.g. "gentle ocean waves crashing at sunset, seagulls in the distance").
- combine_video_audio stops at the shorter stream; keep audio duration \
close to video duration.

## After all tools complete
Summarise what was created: list each output file path and a one-line \
description of its contents.
"""

TOOL_MAP = {
    "generate_image": image_tool.generate_image,
    "generate_video": video_tool.generate_video,
    "generate_tts": audio_tool.generate_tts,
    "generate_sound_effect": audio_tool.generate_sound_effect,
    "combine_video_audio": combine_tool.combine_video_audio,
}


def _build_config() -> types.GenerateContentConfig:
    """Build Gemini config with all tool declarations."""
    schemas = [
        image_tool.SCHEMA,
        video_tool.SCHEMA,
        audio_tool.TTS_SCHEMA,
        audio_tool.SFX_SCHEMA,
        combine_tool.SCHEMA,
    ]
    tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=s["name"],
                description=s["description"],
                parameters=s["parameters"],
            )
            for s in schemas
        ]
    )
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[tool],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )


def run_agent(user_prompt: str) -> None:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = _build_config()

    chat = client.chats.create(model=GEMINI_MODEL, config=config)

    if is_dry_run():
        print("[DRY_RUN] Media API calls will be skipped — fixture files will be written.")

    response = chat.send_message(user_prompt)

    while True:
        # Collect function calls from this response
        fn_calls = [
            p.function_call
            for p in response.candidates[0].content.parts
            if p.function_call and p.function_call.name
        ]

        if not fn_calls:
            # No more tool calls — print the final text and exit
            try:
                print(response.text)
            except Exception:
                pass
            break

        # Execute each tool and send results back
        fn_parts = []
        for call in fn_calls:
            print(f"[tool] {call.name}  args={dict(call.args)}")
            try:
                result = TOOL_MAP[call.name](**dict(call.args))
                print(f"[tool] → {result}")
                fn_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=call.id,
                            name=call.name,
                            response={"result": json.dumps(result)},
                        )
                    )
                )
            except Exception as exc:
                print(f"[tool] ERROR in {call.name}: {exc}", file=sys.stderr)
                fn_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=call.id,
                            name=call.name,
                            response={"error": str(exc)},
                        )
                    )
                )

        response = chat.send_message(fn_parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Free media generation agent: Gemini + FLUX + Replicate + Edge TTS"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help='Creative brief, e.g. "Make a 5-second sunset video with wave sounds"',
    )
    args = parser.parse_args()

    required_keys = ["GEMINI_API_KEY", "HF_TOKEN", "REPLICATE_API_TOKEN"]
    missing = [k for k in required_keys if not os.environ.get(k)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Copy .env.example to .env and fill in your keys.", file=sys.stderr)
        sys.exit(1)

    run_agent(args.prompt)


if __name__ == "__main__":
    main()
