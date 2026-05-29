import asyncio
import os
import subprocess

import edge_tts

from utils import get_hf_client, output_path, is_dry_run, check_ffmpeg

# Full list of voices: run `edge-tts --list-voices` in your terminal
DEFAULT_VOICE = "en-US-JennyNeural"

TTS_SCHEMA = {
    "name": "generate_tts",
    "description": "Generate spoken audio from text using Microsoft Edge TTS (free, no API key needed) and save as MP3.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Text to convert to speech.",
            },
            "voice": {
                "type": "string",
                "description": (
                    "Edge TTS voice name. Default: en-US-JennyNeural (female). "
                    "Other options: en-US-GuyNeural (male), en-GB-SoniaNeural (British female)."
                ),
            },
        },
        "required": ["text"],
    },
}

SFX_SCHEMA = {
    "name": "generate_sound_effect",
    "description": (
        "Generate ambient audio or sound effects using Hugging Face MusicGen (free) and save as MP3. "
        "Good for background music, nature sounds, and ambient audio."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Description of the sound (e.g. 'gentle ocean waves', 'birds chirping in a forest at dawn').",
            },
        },
        "required": ["prompt"],
    },
}


async def _speak(text: str, voice: str, out: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out)


def generate_tts(text: str, voice: str = DEFAULT_VOICE) -> dict:
    out = output_path("tts", "mp3")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_TTS")
        return {"file_path": out}

    asyncio.run(_speak(text, voice, out))
    return {"file_path": out}


def generate_sound_effect(prompt: str) -> dict:
    out = output_path("sfx", "mp3")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_SFX")
        return {"file_path": out}

    check_ffmpeg()
    client = get_hf_client()

    # facebook/musicgen-small generates ambient audio from text descriptions
    audio_bytes = client.text_to_audio(
        prompt,
        model="facebook/musicgen-small",
    )

    # HF returns WAV bytes; convert to MP3 via ffmpeg
    wav_path = out.replace(".mp3", ".wav")
    with open(wav_path, "wb") as f:
        f.write(audio_bytes)

    subprocess.run(
        ["ffmpeg", "-y", "-i", wav_path, out],
        capture_output=True,
        check=True,
    )
    os.remove(wav_path)

    return {"file_path": out}
