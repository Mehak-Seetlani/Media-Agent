import os
import shutil
import time
import anthropic
import openai
from elevenlabs import ElevenLabs

_anthropic_client: anthropic.Anthropic | None = None
_openai_client: openai.OpenAI | None = None
_elevenlabs_client: ElevenLabs | None = None


def get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _anthropic_client


def get_openai() -> openai.OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai_client


def get_elevenlabs() -> ElevenLabs:
    global _elevenlabs_client
    if _elevenlabs_client is None:
        _elevenlabs_client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    return _elevenlabs_client


def output_path(prefix: str, ext: str) -> str:
    os.makedirs("output", exist_ok=True)
    return f"output/{prefix}_{int(time.time())}.{ext}"


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg binary not found on PATH. "
            "Install it with: apt install ffmpeg  (Linux) or brew install ffmpeg  (macOS)"
        )


def is_dry_run() -> bool:
    return os.environ.get("DRY_RUN", "0") == "1"
