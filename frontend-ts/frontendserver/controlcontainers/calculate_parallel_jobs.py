import subprocess
import json
import math
import shutil
import os
location = os.environ.get('CLOUDREGION')

az_path = shutil.which("az")
if not az_path:
    raise RuntimeError("Azure CLI not found in PATH. Run `where az` and use full path instead.")

def filter_cuda_compatible_families(gpu_data):
    cuda_supported_keywords = [
        "NCASv3_T4", "NCADSA10v4", "NCADSA100v4",
        "NDMSv4", "NDASv4"
    ]

    relevant = []
    for entry in gpu_data:
        name = entry["name"]["value"]
        for keyword in cuda_supported_keywords:
            if keyword.lower() in name.lower():
                if int(entry["limit"]) - int(entry["currentValue"])>0:
                    relevant.append({
                        "name": name,
                        "current": int(entry["currentValue"]),
                        "limit": int(entry["limit"]),
                        "available": int(entry["limit"]) - int(entry["currentValue"])
                    })
                break
            
    current = relevant[0]["current"]
    limit = relevant[0]["limit"]
    available = relevant[0]["available"]
    return available, limit, current            


# import calculate_parallel_jobs   
# calculate_parallel_jobs.get_total_vcpu_quota(location="eastus", gpurequest=True) 

def get_total_vcpu_quota(location=location, gpurequest=False):
    cmd = [az_path, "vm", "list-usage", "--location", location, "--output", "json"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        usage_data = json.loads(result.stdout)

        if gpurequest:
            # Filter for GPU-related SKUs in Python instead of JMESPath
            gpu_keywords = ("NC", "ND", "NV")
            gpu_entries = [
                e for e in usage_data
                if any(k in e["name"]["value"] for k in gpu_keywords)
            ]
            return filter_cuda_compatible_families(gpu_entries)  # Optional: return total/limit sum instead if needed

        for entry in usage_data:
            if entry["name"]["localizedValue"] == "Total Regional vCPUs":
                current = int(entry["currentValue"])
                limit = int(entry["limit"])
                available = limit - current
                return available, limit, current

        raise ValueError("Total Regional vCPUs not found in usage list.")

    except subprocess.CalledProcessError as e:
        print("Failed to run az CLI:", e.stderr)
        return None, None, None

def calculate_parallel_pods(vcpu_per_pod=4, location=location, gpurequest=False):
    available, limit, used = get_total_vcpu_quota(location, gpurequest)
    if available is None:
        return
    max_pods = math.floor(available / vcpu_per_pod)
    print(f"Location: {location}")
    print(f"Total vCPU limit: {limit}")
    print(f"vCPUs in use: {used}")
    print(f"Available vCPUs: {available}")
    print(f"→ You can run up to {max_pods} parallel pods with {vcpu_per_pod} vCPUs each.")
    
    return max_pods



