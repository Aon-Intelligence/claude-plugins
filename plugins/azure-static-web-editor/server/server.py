# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "azure-storage-blob>=12.19",
#     "mcp[cli]>=1.2",
#     "openai>=1.40",
#     "Pillow>=10.0",
#     "requests>=2.31",
# ]
# ///
"""MCP server for editing a static website hosted in Azure Blob Storage.

Dependencies are declared inline (PEP 723) so `uv run --script` resolves them
into an ephemeral environment. Clients need `uv`, not a Python setup.
"""
import json

from mcp.server.fastmcp import FastMCP

from blob_container_client import (
    upload_content_to_blob,
    download_contents_from_blob,
    download_bytes_from_blob,
    get_all_files_in_container,
    upload_image_to_blob,
    is_text_file,
)
from image_generator import generate_image_from_prompt, generate_favicon_ico

mcp = FastMCP("static-web-editor")


@mcp.tool()
def get_all_files() -> str:
    """
    Gets a list of all files currently on the website.

    Returns a JSON string of the list of files and their properties
    (name, size, last_modified, content_type).
    """
    return json.dumps(get_all_files_in_container(), indent=2)


@mcp.tool()
def get_file(file_name: str) -> str:
    """
    Gets the contents of a file from the website.

    For text files (HTML, CSS, JS), returns the raw text content.
    For binary files (images), returns base64-encoded content.

    Args:
        file_name (str): The name of the file to retrieve (e.g., "index.html", "images/hero.jpeg")
    """
    return download_contents_from_blob(file_name)


@mcp.tool()
def save_file(file_name: str, content: str) -> str:
    """
    Uploads text content to the website. Overwrites the file if it already exists.

    Use this for HTML, CSS, JavaScript, and other text-based files.
    Do not use this for images — use generate_image instead.

    Args:
        file_name (str): The name of the file to save (e.g., "index.html", "about.html", "styles.css")
        content (str): The full text content to upload
    """
    if not is_text_file(file_name):
        raise ValueError(
            f"'{file_name}' is not a text file. Use generate_image for images."
        )

    upload_content_to_blob(file_name, content)
    return f"File '{file_name}' saved successfully."


@mcp.tool()
def generate_image(prompt: str, file_name: str, size: str = "1024x1024") -> str:
    """
    Generates an image using OpenAI's DALL-E API and uploads it to the website.

    Images are saved to the images/ folder. Always prefix the file_name with "images/".

    Args:
        prompt (str): Detailed description of the image to generate.
            Be specific about style, mood, colors, and composition for best results.
            Examples: "A minimalist hero image with soft blue gradient and abstract geometric shapes",
                      "A professional team photo illustration with diverse people in a modern office"
        file_name (str): Where to save the image. Must use "images/" prefix.
            Examples: "images/hero.jpeg", "images/team-photo.jpeg"
        size (str): Image dimensions. Options: "1024x1024" (square), "1792x1024" (landscape), "1024x1792" (portrait).
            Default: "1024x1024"
    """
    img = generate_image_from_prompt(prompt, size)
    upload_image_to_blob(file_name, img)
    return f"Image generated and saved as '{file_name}'."


@mcp.tool()
def generate_favicon(filename: str) -> str:
    """
    Generates a favicon.ico from an existing image on the website and saves it to the root.

    The source image must already be uploaded to the site (e.g., via generate_image).
    The resulting favicon.ico is placed at the website root automatically.

    Args:
        filename (str): Path to the source image already on the website.
            Examples: "images/logo.jpeg", "images/icon.jpeg"
    """
    image_bytes = download_bytes_from_blob(filename)
    favicon = generate_favicon_ico(image_bytes)
    upload_image_to_blob("favicon.ico", favicon)
    return f"favicon.ico generated from '{filename}' and saved to the website root."


if __name__ == "__main__":
    mcp.run()
