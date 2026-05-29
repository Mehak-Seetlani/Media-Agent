import subprocess
from utils import output_path, check_ffmpeg, is_dry_run

SCHEMA = {
    "name": "combine_video_audio",
    "description": "Merge an MP4 video file and an MP3 audio file into a single MP4.",
    "input_schema": {
        "type": "object",
        "properties": {
            "video_path": {
                "type": "string",
                "description": "Path to the input MP4 video file.",
            },
            "audio_path": {
                "type": "string",
                "description": "Path to the input MP3 audio file.",
            },
            "output_path": {
                "type": "string",
                "description": "Destination path for the combined MP4. Auto-generated if omitted.",
            },
        },
        "required": ["video_path", "audio_path"],
    },
}


def combine_video_audio(
    video_path: str,
    audio_path: str,
    output_path: str | None = None,
) -> dict:
    # Resolve path before any branch that writes to it
    if output_path is None:
        from utils import output_path as make_path
        output_path = make_path("combined", "mp4")

    if is_dry_run():
        with open(output_path, "wb") as f:
            f.write(b"DRY_RUN_COMBINED")
        return {"file_path": output_path}

    check_ffmpeg()

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "copy",   # MP3 passthrough — no re-encode needed
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed (exit {result.returncode}):\n{result.stderr.decode()}"
        )

    return {"file_path": output_path}
