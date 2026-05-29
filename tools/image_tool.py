from utils import get_hf_client, output_path, is_dry_run

SCHEMA = {
    "name": "generate_image",
    "description": "Generate an image using FLUX.1-schnell (via Hugging Face, free) and save as PNG.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Detailed description of the image to generate.",
            },
            "size": {
                "type": "string",
                "description": "Image dimensions. One of: 512x512, 768x768, 1024x1024. Default: 1024x1024.",
                "enum": ["512x512", "768x768", "1024x1024"],
            },
        },
        "required": ["prompt"],
    },
}


def generate_image(prompt: str, size: str = "1024x1024") -> dict:
    out = output_path("image", "png")

    if is_dry_run():
        with open(out, "wb") as f:
            f.write(b"DRY_RUN_IMAGE")
        return {"file_path": out, "prompt_used": prompt}

    width, height = map(int, size.split("x"))
    client = get_hf_client()
    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-schnell",
        width=width,
        height=height,
    )
    image.save(out)

    return {"file_path": out, "prompt_used": prompt}
