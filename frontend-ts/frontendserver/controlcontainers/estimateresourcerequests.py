from azure.identity import DefaultAzureCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.compute import ComputeManagementClient
import requests

url = "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
headers = {"Metadata": "true"}
resp = requests.get(url, headers=headers)
data = resp.json()


# set your subscription + cluster details
subscription_id = data.get('compute').get('subscriptionId')
cluster_name = "ediscovery-aks"
location = data.get('compute').get('location')
resource_group = data.get('compute').get('resourceGroupName').replace('MC','').replace(location,'').replace(cluster_name,'').replace('_','')
resource_group_managed = data.get('compute').get('resourceGroupName')

# authenticate (uses Azure CLI login / Managed Identity inside Cloud Shell)
credential = DefaultAzureCredential()
client = ContainerServiceClient(credential, subscription_id)
clientCompute = ComputeManagementClient(credential, subscription_id)




def getnodeCapabilities(poolname):
    
    node_pools = clientCompute.virtual_machine_scale_sets.list(resource_group_managed)
    
    for pool in node_pools:
        if poolname in pool.name:break
    print(pool.sku.name)

    

    for sku in clientCompute.resource_skus.list(location):
        if location in sku.locations and sku.name==pool.sku.name:
            mem_gb = None
            vcpus = None
            for cap in sku.capabilities:
                if cap.name == "MemoryGB":
                    mem_gb = cap.value
                elif cap.name == "vCPUs":
                    vcpus = cap.value
                    
            break
        
    print(f"Node Pool: {pool.name}, VM Size: {pool.sku.name}, vCPUs: {vcpus}, MemoryGB: {mem_gb}")
    return (vcpus,mem_gb)        