import math
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
location = os.environ.get('CLOUDREGION')

from . import estimateresourcerequests as estimateresourcerequests

    
def get_compute_client():
    credential = DefaultAzureCredential()
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    return ComputeManagementClient(credential, subscription_id)


def filter_cuda_compatible_families(gpu_data):
    cuda_supported_keywords = [
        "NCASv3_T4", "NCADSA10v4", "NCADSA100v4",
        "NDMSv4", "NDASv4"
    ]

    relevant = []
    for entry in gpu_data:
        name = entry.name.value
        for keyword in cuda_supported_keywords:
            if keyword.lower() in name.lower():
                if entry.limit - entry.current_value > 0:
                    relevant.append({
                        "name": name,
                        "current": entry.current_value,
                        "limit": entry.limit,
                        "available": entry.limit - entry.current_value
                    })
                break

    if not relevant:
        raise RuntimeError("No compatible GPU SKUs with quota found.")

    current = relevant[0]["current"]
    limit = relevant[0]["limit"]
    available = relevant[0]["available"]
    return available, limit, current


def get_total_vcpu_quota(location=location, gpurequest=False):
    client = get_compute_client()
    usage_data = list(client.usage.list(location))

    # if gpurequest:
    #     gpu_keywords = ("NC", "ND", "NV")
    #     gpu_entries = [
    #         e for e in usage_data
    #         if any(k in e.name.value for k in gpu_keywords)
    #     ]
    #     return filter_cuda_compatible_families(gpu_entries)

    for entry in usage_data:
        if entry.name.localized_value == "Total Regional vCPUs":
            current = entry.current_value
            limit = entry.limit
            available = limit - current
            return available, limit, current

    raise RuntimeError("Total Regional vCPUs not found.")


def calculate_parallel_pods(location=location, gpucount=0):
    
    node_selector = "gpupool" if gpucount > 0 else "cpupool"
    toleration_key = "gpu-job" if gpucount > 0 else "cpu-job"
    
    gpurequest = True if gpucount > 0 else False

    cpuRequest, memoryRequest = estimateresourcerequests.getnodeCapabilities(node_selector)
        
    available, limit, used = get_total_vcpu_quota(location, gpurequest) 
    if available is None:
        return

    max_pods = math.floor(available / int(cpuRequest))
    print(f"Location: {location}")
    print(f"Total vCPU limit: {limit}")
    print(f"vCPUs in use: {used}")
    print(f"Available vCPUs: {available}")
    print(f"→ You can run up to {max_pods} parallel pods with {cpuRequest} vCPUs each.")
    return max_pods, cpuRequest, memoryRequest
