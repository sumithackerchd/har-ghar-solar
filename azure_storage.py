import os
import uuid

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

from dotenv import load_dotenv

load_dotenv(override=True)
#load_dotenv()

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER")


print("Connection String =", os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
print("Container =", os.getenv("AZURE_STORAGE_CONTAINER"))


blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)

container_client = blob_service_client.get_container_client(container_name)


def upload_file(file):
    """
    Uploads a Flask uploaded file to Azure Blob Storage.
    Returns the Blob URL.
    """

    extension = os.path.splitext(file.filename)[1]

    blob_name = f"{uuid.uuid4()}{extension}"

    blob_client = container_client.get_blob_client(blob_name)

    blob_client.upload_blob(
        file,
        overwrite=True
    )

    return blob_client.url