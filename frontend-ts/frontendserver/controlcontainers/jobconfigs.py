import yaml
from kubernetes import client, config
import textwrap
import os
from time import sleep

ACR_LOGIN_SERVER = os.environ.get("ACR_LOGIN_SERVER")
 
def check_if_pod_running(jobname, namespace="default", timeout=2400, interval=300):
    """
    Check if a pod created by a Job is running in Kubernetes.
    
    :param jobname: Job suffix (without "ediscovery-").
    :param namespace: Namespace of the job.
    :param timeout: Max seconds to wait before giving up.
    :param interval: Seconds between checks.
    :return: "running" | "succeeded" | "failed" | "notfound" | "timeout"
    """
    jobname = jobname.replace("_", "-")
    full_jobname = f"ediscovery-{jobname}"

    config.load_incluster_config()
    core_v1 = client.CoreV1Api()

    waited = 0
    while waited < timeout:
        try:
            pods = core_v1.list_namespaced_pod( namespace=namespace, label_selector=f"job-name={full_jobname}").items

            if not pods:
                print(f"No pods found for job {full_jobname}.")
                pods=[]

            # Check status of pods
            for pod in pods:
                phase = pod.status.phase
                if phase == "Running":
                    print(f"Pod {pod.metadata.name} is running.")
                    return "running"
                elif phase == "Succeeded":
                    print(f"Pod {pod.metadata.name} succeeded.")
                    return "succeeded"
                elif phase == "Failed":
                    print(f"Pod {pod.metadata.name} failed.")
                    return "failed"

            print(f"Pods for {full_jobname} not active yet, retrying in {interval}s...")
            sleep(interval)
            waited += interval

        except client.exceptions.ApiException as e:
            if e.status == 404:
                print(f"Job {full_jobname} does not exist.")
                return "notfound"
            else:
                print(f"Error checking pods: {e}")
                return "error"

    print(f"Timeout reached while waiting for pods of {full_jobname}.")
    return "timeout"

        
            
def generate_k8_job(jobname='jobname', stage='extract', db_name='db_test', bucketname='ediscoveryfiles_test', userinjesttype='', RUNENV='DOCKER', gpucount=0, claimName='vpc', sleeptime=0, cpuRequest=0, memoryRequest=0):
    # Conditionally add GPU limits only if gpucount > 0
    jobname = f"{jobname}".replace("_", "-")
        
    config.load_incluster_config()  # or config.load_kube_config()


    toleration_key = "gpu-job" if gpucount > 0 else "cpu-job"
    
    print(f'cpuRequest: {cpuRequest}, memoryRequest: {memoryRequest}')
    
    cpuRequeststr = str(int(cpuRequest)*.80*1000)+'m' # request 90% of CPU
    memoryRequeststr = str(int(int(memoryRequest)*.83))+'Gi' # request 90% of CPU
    
    cpuRequestLIMIT = str(int(cpuRequest)*1000)+'m' # request 90% of CPU
    memoryRequestLIMIT = str(int(int(memoryRequest)))+'Gi' # request 90% of CPU
    

    print(f'cpuRequest: {cpuRequeststr}, memoryRequest: {memoryRequeststr}')
            
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": f"ediscovery-{jobname}"
        },
        "spec": {
            "ttlSecondsAfterFinished": 60,
            "template": {
                "spec": {
                    "serviceAccountName": "frontend-sa",
                    "restartPolicy": "Never",
                    "tolerations": [
                        {
                            "key": toleration_key,
                            "operator": "Equal",
                            "value": "true",
                            "effect": "NoSchedule"
                        }
                    ],
                    "affinity": {
                        "podAntiAffinity": {
                            "requiredDuringSchedulingIgnoredDuringExecution": [
                                {
                                    "labelSelector": {
                                        "matchExpressions": [
                                            {
                                                "key": "job-name",
                                                "operator": "In",
                                                "values": [f"ediscovery-{jobname}"]
                                            }
                                        ]
                                    },
                                    "topologyKey": "kubernetes.io/hostname"
                                }
                            ]
                        }
                    },
                    "containers": [
                        {
                            "name": "ediscovery",
                            "image": f"{ACR_LOGIN_SERVER}/ediscovery-backend-gpu-image:latest",
                            'imagePullPolicy': 'Always',
                            "args": ["--stage", stage,
                                "--db_name", db_name,
                                "--bucketname", bucketname,
                                "--documentdump", userinjesttype
                            ],
                            "resources": {
                                "requests": {
                                    "memory": memoryRequeststr,
                                    "cpu": cpuRequeststr
                                },
                                "limits": {
                                    "memory": memoryRequestLIMIT,
                                    "cpu": cpuRequestLIMIT
                                }
                            }
                        }
                    ]
                }
            }
        }
    }

    job["spec"]["template"].setdefault("metadata", {}).setdefault("annotations", {})["azure.workload.identity/use"] = "true" 
    job["spec"]["template"].setdefault("metadata", {}).setdefault("labels", {})["azure.workload.identity/use"] = "true" 
    
    job["spec"]["template"]["spec"]["containers"][0]["envFrom"] = [
    {"configMapRef": {"name": "ediscovery-common-env"}},
    {"secretRef":   {"name": "ediscovery-common-secrets"}},
    {"configMapRef": {"name": "ediscovery-static-env"}},
    ]

                            
    if gpucount > 0:
        job["spec"]["template"]["spec"]["tolerations"][0]["key"]       = "nvidia.com/gpu"
        job["spec"]["template"]["spec"]["tolerations"][0]["operator"]  = "Exists"
        job["spec"]["template"]["spec"]["tolerations"][0]["effect"]    = "NoSchedule"
        job["spec"]["template"]["spec"]["tolerations"][0].pop("value", None)
                        
        job["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["nvidia.com/gpu"]   = gpucount
        job["spec"]["template"]["spec"]["containers"][0]["resources"]["requests"]["nvidia.com/gpu"] = gpucount
        
    elif gpucount == 0:
        job["spec"]["template"]["spec"]["affinity"] = {
            "nodeAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [
                        {
                            "matchExpressions": [
                                {
                                    "key": "agentpool",
                                    "operator": "In",
                                    "values": ["cpupool", "gpupool"]  # allow both pools
                                }
                            ]
                        }
                    ]
                },
                "preferredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "weight": 100,
                        "preference": {
                            "matchExpressions": [
                                {
                                    "key": "agentpool",
                                    "operator": "In",
                                    "values": ["cpupool"]  # prefer GPU pool
                                }
                            ]
                        }
                    }
                ]
            }
        }
                
        job["spec"]["template"]["spec"]["tolerations"] = [
            {"key": "cpu-job", "operator": "Equal", "value": "true", "effect": "NoSchedule"},
            {"key": "gpu-job", "operator": "Equal", "value": "true", "effect": "NoSchedule"},
            {"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}
        ]
        
    elif gpucount < 0:
        job["spec"]["template"]["spec"]["affinity"] = {
            "nodeAffinity": {
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [
                        {
                            "matchExpressions": [
                                {
                                    "key": "agentpool",
                                    "operator": "In",
                                    "values": ["cpupool"]  # allow both pools
                                }
                            ]
                        }
                    ]
                },
                "preferredDuringSchedulingIgnoredDuringExecution": [
                    {
                        "weight": 100,
                        "preference": {
                            "matchExpressions": [
                                {
                                    "key": "agentpool",
                                    "operator": "In",
                                    "values": ["cpupool"]  # prefer GPU pool
                                }
                            ]
                        }
                    }
                ]
            }
        }
                
        job["spec"]["template"]["spec"]["tolerations"] = [
            {"key": "cpu-job", "operator": "Equal", "value": "true", "effect": "NoSchedule"}
        ]         
        
        # add volumes (merge, don't overwrite)
        job["spec"]["template"]["spec"].setdefault("volumes", []).append(
            {
                "name": "dshm",
                "emptyDir": {
                    "medium": "Memory",
                    "sizeLimit": "16Gi"
                }
            }
        )

        # add volumeMounts for the first container
        job["spec"]["template"]["spec"]["containers"][0].setdefault("volumeMounts", []).append(
            {
                "mountPath": "/dev/shm",
                "name": "dshm"
            }
        )
                   
        
    batch_v1 = client.BatchV1Api()
    batch_v1.create_namespaced_job(namespace="default", body=job)



    
def run_locally(stage, db_name, bucketname):
    subprocess.run([
        "docker", "run", "--rm",
        "ediscovery-backend-gpu-image",
        "--stage", stage,
        "--db_name", db_name,
        "--bucketname", bucketname
    ])