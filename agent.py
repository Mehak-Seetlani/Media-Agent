#!/usr/bin/env python3
"""
Media generation agent — orchestrates DALL-E 3, Sora-2, and ElevenLabs
via Claude tool-use to fulfil natural language creative briefs.

Usage:
    python agent.py --prompt "Create a 4-second sunset video with ambient waves"
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()

import tools.image_tool as image_tool
import tools.video_tool as video_tool
import tools.audio_tool as audio_tool
import tools.combine_tool as combine_tool
from utils import get_anthropic, is_dry_run

os.makedirs("output", exist_ok=True)

MODEL = "claude-sonnet-4-6"

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
- Expand the user's brief with vivid cinematic or artistic detail when calling \
image/video tools — richer prompts produce better results.
- For sound effects, describe the acoustic environment (e.g. "gentle ocean \
waves at sunset with distant seagulls").
- combine_video_audio stops at the shorter stream; match audio duration to \
video duration when possible.

## After all tools complete
Summarise what was created: list each output file path and a one-line \
description of its contents.
"""

# Tool definitions with prompt caching on the last entry
TOOLS = [
    image_tool.SCHEMA,
    video_tool.SCHEMA,
    audio_tool.TTS_SCHEMA,
    audio_tool.SFX_SCHEMA,
    {**combine_tool.SCHEMA, "cache_control": {"type": "ephemeral"}},
]

TOOL_MAP = {
    "generate_image": image_tool.generate_image,
    "generate_video": video_tool.generate_video,
    "generate_tts": audio_tool.generate_tts,
    "generate_sound_effect": audio_tool.generate_sound_effect,
    "combine_video_audio": combine_tool.combine_video_audio,
}


def run_agent(user_prompt: str) -> None:
    client = get_anthropic()

    system = [
        {
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ]

    messages: list[dict] = [{"role": "user", "content": user_prompt}]

    if is_dry_run():
        print("[DRY_RUN] API calls will be skipped — fixture files will be written.")

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        # Serialise to plain dicts so the messages list stays JSON-safe across turns
        messages.append(
            {"role": "assistant", "content": [b.model_dump() for b in response.content]}
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                print(f"[tool] {block.name}  args={json.dumps(block.input, ensure_ascii=False)}")
                try:
                    result = TOOL_MAP[block.name](**block.input)
                    print(f"[tool] → {result}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result),
                        }
                    )
                except Exception as exc:
                    print(f"[tool] ERROR in {block.name}: {exc}", file=sys.stderr)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps({"error": str(exc)}),
                            "is_error": True,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason!r}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Media generation agent powered by Claude + DALL-E 3 + Sora-2 + ElevenLabs"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help='Creative brief, e.g. "Make a 4-second sunset video with ambient waves"',
    )
    args = parser.parse_args()

    # Validate required keys here, not at import time, so the module is importable in tests
    required_keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
    missing = [k for k in required_keys if not os.environ.get(k)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Copy .env.example to .env and fill in your keys.", file=sys.stderr)
        sys.exit(1)

    run_agent(args.prompt)


if __name__ == "__main__":
    main()
