from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
import os


def yield_blob_bytes(container_name=None, max_workers=1, process_fn=None):
    """
    Download blobs from Azure.
    
    Args:
        container_name (str): Name of container. Defaults to env BUCKETNAME.
        max_workers (int): Degree of parallelism. 
                           1 = sequential, >1 = parallel threads.
        process_fn (callable): Optional function (name, bytes) -> result.
                               If None, yields raw (name, bytes).
    
    Yields:
        (blob_name, result) for each blob.
    """
    credential = DefaultAzureCredential()
    account_url = os.environ["AZURE_BLOB_ACCOUNT_URL"]
    container_client = BlobServiceClient(
        account_url=account_url, credential=credential
    ).get_container_client(container_name or os.environ["BUCKETNAME"])

    blob_names = [b.name for b in container_client.list_blobs()]

    def _download_and_process(blob_name):
        blob_client = container_client.get_blob_client(blob_name)
        blob_bytes = blob_client.download_blob(max_concurrency=4).readall()
        if process_fn:
            return blob_name, process_fn(blob_name, blob_bytes)
        return blob_name, blob_bytes

    if max_workers == 1:  # sequential
        for name in blob_names:
            yield _download_and_process(name)
    else:  # parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(_download_and_process, name): name for name in blob_names}
            for future in as_completed(futures):
                yield future.result()

def getbloblist(container_name=None):        
    credential = DefaultAzureCredential()
    account_url = os.environ["AZURE_BLOB_ACCOUNT_URL"]
    container_client = BlobServiceClient(
        account_url=account_url, credential=credential
    ).get_container_client(container_name or os.environ["BUCKETNAME"])

    blob_names = [b.name for b in container_client.list_blobs()]
    
    return blob_names, container_client
    
def getblobbytes(container_client, blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_bytes = blob_client.download_blob(max_concurrency=4).readall()
        
    return blob_bytes