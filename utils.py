import os
import shutil
import time

from huggingface_hub import InferenceClient

_hf_client: InferenceClient | None = None


def get_hf_client() -> InferenceClient:
    global _hf_client
    if _hf_client is None:
        _hf_client = InferenceClient(token=os.environ["HF_TOKEN"])
    return _hf_client


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
