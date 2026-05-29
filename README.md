# Media Agent — 100% Free Stack

A CLI agent that generates images, videos, and audio from natural language prompts using **entirely free APIs**.

| Component | Service | Cost |
|---|---|---|
| Orchestration | **Google Gemini 2.0 Flash** | Free (1,500 req/day) |
| Images | **FLUX.1-schnell** via Hugging Face | Free |
| Video | **minimax/video-01** via Replicate | $5 free credit (~15 videos) |
| Speech (TTS) | **Microsoft Edge TTS** | Free, no API key |
| Sound effects | **MusicGen** via Hugging Face | Free |
| A/V merge | **ffmpeg** (local) | Free |

## How it works

You describe what you want in plain language. Gemini decides which tools to call, then executes the full pipeline — generating video, audio, and merging them into a final MP4.

```
python agent.py --prompt "Make a video of a magical forest with ambient birdsong"
```

```
[tool] generate_video  args={'prompt': 'A lush magical forest...'}
[tool] → {'file_path': 'output/video_1748476800.mp4'}
[tool] generate_sound_effect  args={'prompt': 'birds chirping in a forest, gentle wind'}
[tool] → {'file_path': 'output/sfx_1748476830.mp3'}
[tool] combine_video_audio  args={...}
[tool] → {'file_path': 'output/combined_1748476840.mp4'}

Created:
- output/combined_1748476840.mp4 — magical forest video with ambient birdsong
```

## Setup (step by step)

### Step 1 — Get your API keys (all free)

**A. Google Gemini API Key**
1. Go to **aistudio.google.com**
2. Sign in with your Google account
3. Click **Get API key** → **Create API key**
4. Copy it — looks like `AIzaSy...`

**B. Hugging Face Token**
1. Go to **huggingface.co** → Sign up (free)
2. Click your profile picture → **Settings** → **Access Tokens**
3. Click **New token** → Name it anything → Role: **Read** → Generate
4. Copy it — looks like `hf_...`

**C. Replicate API Token** (video generation — $5 free credit)
1. Go to **replicate.com** → Sign up (free)
2. Click your profile → **API tokens**
3. Copy your token — looks like `r8_...`
4. You get $5 free credit automatically (~15 videos at ~$0.30 each)

---

### Step 2 — Install Python

1. Go to **python.org/downloads**
2. Download Python **3.11** or newer
3. During install, **check "Add Python to PATH"**

---

### Step 3 — Install ffmpeg

**Windows:**
1. Download from **gyan.dev/ffmpeg/builds** (click "ffmpeg-release-essentials.zip")
2. Extract → copy the path to the `bin` folder (e.g. `C:\ffmpeg\bin`)
3. Search "Edit environment variables" in Windows → System Variables → Path → New → paste the path

**Mac:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install ffmpeg
```

---

### Step 4 — Download this project

```bash
git clone https://github.com/Mehak-Seetlani/Media-Agent.git
cd Media-Agent
git checkout claude/intelligent-rubin-2tkGA
```

---

### Step 5 — Install Python packages

```bash
pip install -r requirements.txt
```

---

### Step 6 — Set up your API keys

```bash
cp .env.example .env
```

Open `.env` in Notepad (Windows) or any text editor and fill in your keys:
```
GEMINI_API_KEY=AIzaSy...your key here...
HF_TOKEN=hf_...your token here...
REPLICATE_API_TOKEN=r8_...your token here...
```

---

### Step 7 — Run!

```bash
python agent.py --prompt "YOUR PROMPT HERE"
```

All output files are saved to the `output/` folder.

---

## Example prompts

```bash
# Generate an image
python agent.py --prompt "Draw a friendly cartoon dragon wearing a graduation cap"

# Children's poem video
python agent.py --prompt "Create a video of a smiling sun in a blue sky with a narrator saying: Twinkle twinkle little star, how I wonder what you are"

# Educational content
python agent.py --prompt "Generate an image explaining the water cycle with labels"

# Ambient video with sound
python agent.py --prompt "Make a video of a cozy fireplace with crackling fire sounds"

# Nature video
python agent.py --prompt "Create a video of ocean waves at sunset with relaxing wave sounds"

# Character illustration
python agent.py --prompt "Draw a brave little knight with shiny armour standing in front of a castle"
```

## Test without spending credits (Dry Run)

```bash
DRY_RUN=1 python agent.py --prompt "Test the pipeline"
```

This runs the full pipeline but skips all API calls — useful for checking your setup works.

---

## Architecture

```
agent.py              Gemini 2.0 Flash orchestrator + tool-use loop
utils.py              Shared HF client, output_path helper, ffmpeg check
tools/
  image_tool.py       FLUX.1-schnell (HuggingFace) → PNG
  video_tool.py       minimax/video-01 (Replicate) → MP4
  audio_tool.py       Edge TTS → MP3  |  MusicGen (HuggingFace) → MP3
  combine_tool.py     ffmpeg video+audio merge → MP4
output/               Your generated files appear here
```

## Notes

- Video clips are approximately **5 seconds** long (minimax/video-01 fixed length)
- For longer videos, run multiple prompts and join with a video editor
- The Replicate $5 free credit gives you roughly **15 videos**
- Edge TTS requires an internet connection but uses no API key or credits
- Generated files are saved with timestamps so they never overwrite each other
