# connect to azure blob storage for writing and reading files
import os
import mimetypes
import base64
from typing import List, Dict, Any

from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings

# Azure's static website feature always serves from a container named "$web".
DEFAULT_CONTAINER = "$web"

# Site backups are stored under this prefix and excluded from live-site operations.
BACKUP_PREFIX = "backups/"

# Extensions mimetypes maps to a non-"text/" type but that are text on disk.
_TEXT_CONTENT_TYPES = {
    "application/javascript",
    "application/json",
    "application/xml",
    "image/svg+xml",
}


def is_text_file(file_name: str) -> bool:
    """Whether a blob should round-trip as UTF-8 text rather than base64."""
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        return False
    return content_type.startswith("text/") or content_type in _TEXT_CONTENT_TYPES


def _container() -> ContainerClient:
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError(
            "Missing AZURE_STORAGE_CONNECTION_STRING. "
            "Set it in plugins/azure-static-web-editor/.env and restart the server."
        )

    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME") or DEFAULT_CONTAINER

    service = BlobServiceClient.from_connection_string(
        connection_string,
        connection_timeout=30,
        read_timeout=30,
    )
    return service.get_container_client(container_name)


def upload_content_to_blob(file_name: str, content: str) -> str:
    """
    Upload text content to Azure Blob Storage with a specified file name.

    Args:
        file_name (str): The name to give the file in blob storage
        content (str): The string content to upload

    Returns:
        str: The final file name used
    """
    blob_client = _container().get_blob_client(file_name)
    content_type = mimetypes.guess_type(file_name)[0]

    if content_type:
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
            timeout=60,
        )
    else:
        blob_client.upload_blob(content, overwrite=True, timeout=60)

    return file_name


def upload_image_to_blob(file_name: str, image_bytes: bytes) -> None:
    """
    Upload image bytes to Azure Blob Storage with a specified file name.

    Args:
        file_name (str): The name to give the file in blob storage
        image_bytes (bytes): The image bytes to upload
    """
    blob_client = _container().get_blob_client(file_name)

    # Detect content type from filename so .ico files get the right type
    content_type = mimetypes.guess_type(file_name)[0] or "image/jpeg"
    blob_client.upload_blob(
        image_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
        timeout=60,
    )


def download_bytes_from_blob(file_name: str) -> bytes:
    """
    Download the raw bytes of a blob.

    Args:
        file_name (str): The name of the file to download from blob storage

    Returns:
        bytes: The blob's raw content
    """
    return _container().get_blob_client(file_name).download_blob().readall()


def download_contents_from_blob(file_name: str) -> str:
    """
    Download a blob as a string.

    Text files decode as UTF-8. Everything else is base64-encoded, since MCP
    responses are JSON and cannot carry raw bytes.

    Args:
        file_name (str): The name of the file to download from blob storage

    Returns:
        str: UTF-8 text for text files, base64 for binary files
    """
    content = download_bytes_from_blob(file_name)

    if is_text_file(file_name):
        return content.decode("utf-8")
    return base64.b64encode(content).decode("ascii")


def _is_backup_path(blob_name: str) -> bool:
    return blob_name == BACKUP_PREFIX.rstrip("/") or blob_name.startswith(BACKUP_PREFIX)


def list_blob_names(prefix: str | None = None) -> List[str]:
    """List blob names in the container, optionally filtered by prefix."""
    container = _container()
    if prefix:
        return [blob.name for blob in container.list_blobs(name_starts_with=prefix)]
    return [blob.name for blob in container.list_blobs()]


def copy_blob_in_container(source_name: str, dest_name: str) -> None:
    """Copy a blob to another path within the same container."""
    container = _container()
    source_client = container.get_blob_client(source_name)
    props = source_client.get_blob_properties()
    content_type = (
        props.content_settings.content_type
        if props.content_settings and props.content_settings.content_type
        else None
    )
    data = source_client.download_blob().readall()

    dest_client = container.get_blob_client(dest_name)
    if content_type:
        dest_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
            timeout=60,
        )
    else:
        dest_client.upload_blob(data, overwrite=True, timeout=60)


def delete_blob(file_name: str) -> None:
    """Delete a blob from the container."""
    _container().delete_blob(file_name)


def get_all_files_in_container() -> List[Dict[str, Any]]:
    """
    Get all files in a blob storage container.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing blob information
    """
    simplified_blob_list = []
    for blob in _container().list_blobs():
        if _is_backup_path(blob.name):
            continue
        blob_info = {
            "name": blob.name,
            "size": blob.size,
            "content_type": (
                blob.content_settings.content_type
                if hasattr(blob, "content_settings") and blob.content_settings
                else "Unknown"
            ),
            "last_modified": (
                blob.last_modified.isoformat()
                if hasattr(blob, "last_modified") and blob.last_modified
                else None
            ),
            "creation_time": (
                blob.creation_time.isoformat()
                if hasattr(blob, "creation_time") and blob.creation_time
                else None
            ),
        }
        simplified_blob_list.append(blob_info)

    return simplified_blob_list
