import io
import os
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "models"
storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT", "rgocfunctionstreamla6b3")

# Crée un client vers le compte de stockage en s'authentifiant via DefaultAzureCredential
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=credential
)

def load_clicks_csv():
    """
    Télécharge clicks_sample.csv depuis le conteneur "models" 
    puis retourne un DataFrame Pandas.
    """
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob="clicks_sample.csv"
    )
    data = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))
    return df






