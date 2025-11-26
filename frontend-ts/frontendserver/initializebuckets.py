import json
from azure.identity import DefaultAzureCredential, CredentialUnavailableError

from azure.storage.blob import BlobServiceClient
import os
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobClient


ISTHISDEMO = os.getenv('ISTHISDEMO')
if ISTHISDEMO != 'True':selectionfile="selectionmap.json"
else:selectionfile="selectionmapdemo.json"


local_file = "useasunderlyingTest_subset.7z"
container_name = "ediscoveryfileslivedemo"  # pick from your containerlist
    
def initializebuckets():
    account_url = os.environ.get("AZURE_BLOB_ACCOUNT_URL")
    
    # No Azure config → skip silently
    print("DEBUG AZURE_BLOB_ACCOUNT_URL:", repr(account_url))
    if not account_url:
                
        print("AZURE_BLOB_ACCOUNT_URL not set; skipping Azure bucket initialization.")
        return
        
    # 2) Try to get credentials; if not available → skip
    try:
        credential = DefaultAzureCredential()
    except CredentialUnavailableError as e:
        print(f"Azure credentials unavailable ({e}); skipping Azure bucket initialization.")
        return
    
        
    # Load from file
    with open(selectionfile, "r") as f:
        selectionmap=json.load(f)

    containerlist = [data['bucket'] for proj, data in selectionmap.items()]
    blob_service = BlobServiceClient(account_url=account_url, credential=credential)

    
    for name in set(containerlist):  # de-dupe if needed
        cc = blob_service.get_container_client(name)
        try:
            cc.get_container_properties()  # exists
            print(f"Container exists: {name}")
        except ResourceNotFoundError:
            try: 
                blob_service.create_container(name)
                print(f"Created container: {name}")
                if name==container_name:
                    movedemofile(blob_service)
            except ResourceExistsError:
                print(f"Raced, already exists: {name}")
                
                

def movedemofile(blob_service):

    blob_name = os.path.basename(local_file)

    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)

    with open(local_file, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    print(f"Uploaded {local_file} to container {container_name} as {blob_name}")
        