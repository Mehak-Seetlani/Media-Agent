# Media Agent

A CLI agent that generates images, videos, and audio from natural language prompts. Powered by **Claude** (orchestration), **DALL-E 3** (images), **Sora-2** (video), and **ElevenLabs** (TTS + sound effects).

## How it works

You describe what you want in plain language. Claude decides which tools to call and in what order, then executes the full pipeline — generating video, creating audio, and merging them into a final MP4.

```
python agent.py --prompt "Create an 8-second cinematic sunrise video with ambient birdsong"
```

```
[tool] generate_video  args={"prompt": "...", "seconds": 8, "size": "1280x720"}
[tool] → {"file_path": "output/video_1748476800.mp4", "video_id": "..."}
[tool] generate_sound_effect  args={"prompt": "birds at dawn...", "duration": 8.0}
[tool] → {"file_path": "output/sfx_1748476815.mp3"}
[tool] combine_video_audio  args={...}
[tool] → {"file_path": "output/combined_1748476820.mp4"}

Created:
- output/combined_1748476820.mp4 — 8-second sunrise video with ambient dawn soundscape
```

## Setup

### 1. Prerequisites

- Python 3.11+
- `ffmpeg` on your PATH
  - macOS: `brew install ffmpeg`
  - Linux: `apt install ffmpeg`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

You need:
| Key | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `OPENAI_API_KEY` | platform.openai.com — requires Sora access |
| `ELEVENLABS_API_KEY` | elevenlabs.io |

### 4. Run

```bash
python agent.py --prompt "YOUR PROMPT"
```

All generated files are saved to the `output/` directory.

## Example prompts

```bash
# Image only
python agent.py --prompt "Generate a hyper-realistic photo of a misty Japanese forest at dawn"

# Video with ambient sound
python agent.py --prompt "Create a 4-second video of rain on a city window with rain sounds"

# Narrated video
python agent.py --prompt "Make an 8-second video of Northern Lights with a narrator saying: The aurora dances tonight"

# Sound effect only
python agent.py --prompt "Generate 10 seconds of a crackling fireplace"
```

## Dry run (no API calls)

Set `DRY_RUN=1` in your `.env` to run the full pipeline without spending credits. Fixture files are written to `output/` so you can verify the flow end-to-end.

```bash
DRY_RUN=1 python agent.py --prompt "Test the pipeline"
```

## Architecture

```
agent.py              Claude orchestrator + agentic tool-use loop
utils.py              Shared API clients, output_path helper, ffmpeg check
tools/
  image_tool.py       DALL-E 3 → PNG
  video_tool.py       Sora-2 → MP4 (with polling + timeout)
  audio_tool.py       ElevenLabs TTS + sound effects → MP3
  combine_tool.py     ffmpeg video+audio merge → MP4
output/               Generated files land here
```

## Notes

- Video generation via Sora can take **2–10 minutes**. The agent polls with exponential backoff and enforces a 20-minute timeout.
- ElevenLabs `eleven_v3` TTS model has a 3,000-character limit per call.
- The Sora API is scheduled for deprecation in September 2026.
