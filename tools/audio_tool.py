import os
from utils import get_elevenlabs, output_path, is_dry_run

TTS_MAX_CHARS = 3000
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # ElevenLabs "George"

TTS_SCHEMA = {
    "name": "generate_tts",
    "description": "Generate spoken audio from text using ElevenLabs TTS and save as MP3.",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": f"Text to synthesise (max {TTS_MAX_CHARS} characters).",
            },
            "voice_id": {
                "type": "string",
                "description": "ElevenLabs voice ID. Uses ELEVENLABS_VOICE_ID env var if omitted.",
            },
        },
        "required": ["text"],
    },
}

SFX_SCHEMA = {
    "name": "generate_sound_effect",
    "description": "Generate a sound effect or ambient audio using ElevenLabs and save as MP3.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Description of the sound to generate (e.g. 'gentle ocean waves at sunset').",
            },
            "duration": {
                "type": "number",
                "description": "Duration in seconds (0.5–30). Default: 5.0.",
            },
            "loop": {
                "type": "boolean",
                "description": "Whether the sound should loop seamlessly. Default: false.",
            },
        },
        "required": ["prompt"],
    },
}


def generate_tts(text: str, voice_id: str | None = None) -> dict:
    if len(text) > TTS_MAX_CHARS:
        raise ValueError(
            f"Text exceeds ElevenLabs eleven_v3 limit of {TTS_MAX_CHARS} characters "
            f"({len(text)} provided). Split into smaller segments."
        )

    out = output_path("tts", "mp3")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_TTS")
        return {"file_path": out}

    resolved_voice = voice_id or os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE_ID)
    client = get_elevenlabs()

    audio_iter = client.text_to_speech.convert(
        voice_id=resolved_voice,
        text=text,
        model_id="eleven_v3",
        output_format="mp3_44100_128",
    )
    with open(out, "wb") as f:
        for chunk in audio_iter:
            f.write(chunk)

    return {"file_path": out}


def generate_sound_effect(
    prompt: str,
    duration: float = 5.0,
    loop: bool = False,
) -> dict:
    duration = float(duration)
    if not (0.5 <= duration <= 30.0):
        raise ValueError(f"duration must be between 0.5 and 30.0 seconds (got {duration})")

    out = output_path("sfx", "mp3")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_SFX")
        return {"file_path": out}

    client = get_elevenlabs()

    # loop is only supported by eleven_text_to_sound_v2
    model_id = "eleven_text_to_sound_v2" if loop else None

    kwargs: dict = dict(
        text=prompt,
        duration_seconds=duration,
        prompt_influence=0.3,
    )
    if loop:
        kwargs["loop"] = True
    if model_id:
        kwargs["model_id"] = model_id

    sfx_iter = client.text_to_sound_effects.convert(**kwargs)
    with open(out, "wb") as f:
        for chunk in sfx_iter:
            f.write(chunk)

    return {"file_path": out}
