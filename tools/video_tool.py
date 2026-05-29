import time
import warnings
from utils import get_openai, output_path, is_dry_run

POLL_INITIAL = 15
POLL_MAX = 30
TIMEOUT_SECONDS = 1200  # 20 minutes

SCHEMA = {
    "name": "generate_video",
    "description": "Generate a video using OpenAI Sora-2 and save it as an MP4 file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed cinematic description of the video to generate.",
            },
            "seconds": {
                "type": "integer",
                "enum": [4, 8, 12],
                "description": "Video duration in seconds. Default: 4.",
            },
            "size": {
                "type": "string",
                "enum": ["1280x720", "720x1280", "1792x1024", "1024x1792"],
                "description": "Video resolution. Default: 1280x720 (landscape HD).",
            },
        },
        "required": ["prompt"],
    },
}


def generate_video(
    prompt: str,
    seconds: int = 4,
    size: str = "1280x720",
) -> dict:
    warnings.warn(
        "OpenAI Sora API is deprecated and will be removed in September 2026.",
        DeprecationWarning,
        stacklevel=2,
    )

    out = output_path("video", "mp4")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_VIDEO")
        return {"file_path": out, "video_id": "dry_run"}

    client = get_openai()

    video_job = client.videos.create(
        model="sora-2",
        prompt=prompt,
        seconds=seconds,
        size=size,
    )

    deadline = time.time() + TIMEOUT_SECONDS
    interval = POLL_INITIAL

    while True:
        if time.time() > deadline:
            try:
                client.videos.delete(video_job.id)
            except Exception:
                pass
            raise TimeoutError(
                f"Sora video generation timed out after {TIMEOUT_SECONDS // 60} minutes "
                f"(job {video_job.id})"
            )

        status = client.videos.retrieve(video_job.id)

        if status.status == "completed":
            break
        elif status.status == "failed":
            raise RuntimeError(
                f"Sora video generation failed (job {video_job.id}): {getattr(status, 'error', 'unknown error')}"
            )
        elif status.status not in ("queued", "in_progress"):
            raise RuntimeError(f"Unexpected Sora job status: {status.status!r}")

        time.sleep(interval)
        interval = min(interval * 1.5, POLL_MAX)

    content = client.videos.download_content(video_job.id, variant="video")
    content.write_to_file(out)

    return {"file_path": out, "video_id": video_job.id}
