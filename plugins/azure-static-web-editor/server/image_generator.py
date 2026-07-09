from openai import OpenAI
import base64
import requests
import os
from PIL import Image
from io import BytesIO


def generate_image_from_prompt(prompt: str, size: str = "1024x1024") -> bytes:
    """
    Generate an image from a prompt using OpenAI's DALL-E API.

    Args:
        prompt (str): Description of the image to generate
        size (str): Size of the image (e.g., "1024x1024", "1792x1024", "1024x1792")

    Returns:
        bytes: Binary image data
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    result = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        response_format="b64_json",
    )

    if hasattr(result.data[0], "b64_json") and result.data[0].b64_json:
        image_bytes = base64.b64decode(result.data[0].b64_json)
    elif hasattr(result.data[0], "url") and result.data[0].url:
        response = requests.get(result.data[0].url)
        image_bytes = response.content
    else:
        raise ValueError("No image data returned from OpenAI API")

    return image_bytes


def generate_favicon_ico(image_bytes: bytes) -> bytes:
    """
    Convert image bytes into a multi-resolution .ico file.

    Args:
        image_bytes (bytes): Source image data (JPEG, PNG, etc.)

    Returns:
        bytes: ICO file data with sizes 16x16 through 256x256
    """
    input_buffer = BytesIO(image_bytes)
    img = Image.open(input_buffer)

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    buffer = BytesIO()
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(buffer, format="ICO", sizes=icon_sizes)

    return buffer.getvalue()
