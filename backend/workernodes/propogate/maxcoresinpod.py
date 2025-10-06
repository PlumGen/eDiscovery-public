import os

def get_effective_cpus():
    # cgroup v1
    quota_v1 = "/sys/fs/cgroup/cpu/cpu.cfs_quota_us"
    period_v1 = "/sys/fs/cgroup/cpu/cpu.cfs_period_us"

    # cgroup v2
    cpu_max_v2 = "/sys/fs/cgroup/cpu.max"

    try:
        if os.path.exists(cpu_max_v2):
            with open(cpu_max_v2, "r") as f:
                quota, period = f.read().strip().split()
                if quota == "max":
                    return os.cpu_count()
                return int(quota) / int(period)
        elif os.path.exists(quota_v1) and os.path.exists(period_v1):
            with open(quota_v1, "r") as f:
                quota = int(f.read())
            with open(period_v1, "r") as f:
                period = int(f.read())
            if quota > 0 and period > 0:
                return quota / period
    except Exception as e:
        print(f"Error reading cgroup info: {e}")

    return os.cpu_count()

print("Effective CPUs:", get_effective_cpus())
