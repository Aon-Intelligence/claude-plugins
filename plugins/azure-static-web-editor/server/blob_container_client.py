# connect to azure blob storage for writing and reading files
import os
import mimetypes
import base64
import time
from typing import List, Dict, Any, Union, Optional
from azure.storage.blob import BlobServiceClient, ContentSettings


def upload_content_to_blob(file_name: str, content: str) -> str:
    """
    Upload text content to Azure Blob Storage with a specified file name.

    Args:
        file_name (str): The name to give the file in blob storage
        content (str): The string content to upload

    Returns:
        str: The final file name used
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER_NAME environment variables")

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string,
        connection_timeout=30,
        read_timeout=30,
    )

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
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
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER_NAME environment variables")

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string,
        connection_timeout=30,
        read_timeout=30,
    )

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    # Detect content type from filename so .ico files get the right type
    content_type = mimetypes.guess_type(file_name)[0] or "image/jpeg"
    blob_client.upload_blob(
        image_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type=content_type),
    )


def download_contents_from_blob(file_name: str) -> Union[str, bytes]:
    """
    Download content from blob storage with a specific file name.

    Args:
        file_name (str): The name of the file to download from blob storage

    Returns:
        Union[str, bytes]: Base64-encoded string for JPEG files, raw content for others
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER_NAME environment variables")

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string,
        connection_timeout=30,
        read_timeout=30,
    )
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    content = blob_client.download_blob().readall()

    if file_name.endswith(".jpeg"):
        return base64.b64encode(content).decode("utf-8")
    else:
        return content


def get_all_files_in_container() -> List[Dict[str, Any]]:
    """
    Get all files in a blob storage container.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing blob information
    """
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

    if not connection_string or not container_name:
        raise ValueError("Missing AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_CONTAINER_NAME environment variables")

    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string,
        connection_timeout=30,
        read_timeout=30,
    )
    container_client = blob_service_client.get_container_client(container_name)

    simplified_blob_list = []
    for blob in container_client.list_blobs():
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
