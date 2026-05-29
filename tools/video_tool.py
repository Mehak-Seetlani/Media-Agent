import urllib.request

import replicate

from utils import output_path, is_dry_run

SCHEMA = {
    "name": "generate_video",
    "description": (
        "Generate a ~5-second video using Replicate (minimax/video-01, uses ~$0.30 of free credit) "
        "and save as MP4."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed cinematic description of the video to generate.",
            },
        },
        "required": ["prompt"],
    },
}


def generate_video(prompt: str) -> dict:
    out = output_path("video", "mp4")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_VIDEO")
        return {"file_path": out}

    # REPLICATE_API_TOKEN is read automatically from env by the replicate library
    output = replicate.run(
        "minimax/video-01",
        input={"prompt": prompt},
    )
    video_url = str(output)
    urllib.request.urlretrieve(video_url, out)

    return {"file_path": out}
