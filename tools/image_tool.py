import base64
from utils import get_openai, output_path, is_dry_run

SCHEMA = {
    "name": "generate_image",
    "description": "Generate an image using DALL-E 3 and save it as a PNG file.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate.",
            },
            "size": {
                "type": "string",
                "enum": ["1024x1024", "1792x1024", "1024x1792"],
                "description": "Image dimensions. Default: 1024x1024.",
            },
            "quality": {
                "type": "string",
                "enum": ["standard", "hd"],
                "description": "Image quality. 'hd' produces finer detail. Default: standard.",
            },
            "style": {
                "type": "string",
                "enum": ["vivid", "natural"],
                "description": "Vivid is hyper-real; natural is more photographic. Default: vivid.",
            },
        },
        "required": ["prompt"],
    },
}


def generate_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid",
) -> dict:
    out = output_path("image", "png")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_IMAGE")
        return {"file_path": out, "prompt_used": prompt}

    client = get_openai()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size=size,
        quality=quality,
        style=style,
        response_format="b64_json",
    )
    image_data = base64.b64decode(response.data[0].b64_json)
    with open(out, "wb") as f:
        f.write(image_data)

    return {"file_path": out, "prompt_used": response.data[0].revised_prompt or prompt}
