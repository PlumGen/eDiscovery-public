#!/usr/bin/env bash
set -Eeuo pipefail
trap 'rc=$?; echo "[preflight] ERROR line $LINENO exit $rc" >&2; exit $rc' ERR

echo "[preflight] Checking provider registrations in subscription: $SUB_ID"
az account set -s "$SUB_ID"

# --- Provider registrations ---

echo '[preflight] checking provider registrations' >&2

# Split the comma-separated REQUIRED into an array
IFS=',' read -r -a need_providers <<< "$REQUIRED"

missing_reg=()
for ns in "${need_providers[@]}"; do
  ns="${ns//[[:space:]]/}"           # trim any stray spaces
  [[ -z "$ns" ]] && continue
  st=$(az provider show -n "$ns" --query registrationState -o tsv 2>/dev/null || echo NotRegistered)
  printf "%-35s %s\n" "$ns" "$st"
  [[ "$st" != "Registered" ]] && missing_reg+=("$ns")
done

if ((${#missing_reg[@]})); then
  msg="Required resource providers not registered: ${missing_reg[*]}. Ask a subscription admin to run: for ns in ${missing_reg[*]}; do az provider register --namespace \$ns; done"
  miss_json="$(printf '"%s",' "${missing_reg[@]}")"; miss_json="[${miss_json%,}]"
  echo "$msg" >&2
  allRegistered="false"
else
  allRegistered="true"
fi

# --- VM size / quota checks ---
# Expected VM size from env, fallback default
#### VM Size Check
check_vm_quota() {
  local size="$1"
  local location="$2"
  local sub_id="$3"

  # 1. Find the family for this size
  local family=$(az rest \
    --method get \
    --url "https://management.azure.com/subscriptions/$sub_id/providers/Microsoft.Compute/skus?api-version=2023-07-01&`echo '$'`filter=location eq '$location'" \
    --query "value[?name=='$size'] | [0].family" \
    -o tsv)

  if [ -z "$family" ]; then
    echo "❌ Could not determine family for $size"
    return 1
  fi

  # 2. Get usage info for that family
  read -r current limit <<<$(az vm list-usage \
    --location "$location" \
    --subscription "$sub_id" \
    --query "[?name.value=='${family}'].[currentValue, limit]" \
    -o tsv)

  if [ -z "$limit" ]; then
    echo "❌ No usage info for family $family"
    return 1
  fi

  # 3. Compute remaining in Bash
  local remaining=$((limit - current))

  # 4. Report availability
  if [ "$remaining" -ge 1 ]; then
    echo "✅ $size available (family: $family, remaining: $remaining)"
    return 0
  else
    echo "❌ No quota for $size (family: $family, remaining: $remaining)"
    return 1
  fi
}


all_ok="true"
missing=()
present=()
gpu_quota_json="[]"
VM_VARS=("$AKSCOMPUTEDEFAULT" "$AKSCOMPUTECPU" "$AKSCOMPUTEGPU")

DISPLAY_LOC=$(az account list-locations --query "[?name=='${LOCATION}'] | [0].displayName" -o tsv)

echo "$LOCATION"
echo "$DISPLAY_LOC"


echo '[preflight] checking required VMs' >&2


for size in "${VM_VARS[@]}"; do
  echo "[preflight] Checking VM size availability: $size in $LOCATION"

  if check_vm_quota "$size" "$LOCATION" "$SUB_ID"; then

    echo "[preflight] VM size $size is AVAILABLE in $LOCATION"
    present+=("$size")

  else
      echo "[preflight] VM size $size is NOT available in $LOCATION"
      all_ok=false
      missing+=("$size")
  fi

done


# Final JSON
# Safely convert Bash array (even if empty) into JSON array
missing_reg_json=$(printf '%s\n' "${missing_reg[@]}" | jq -R . | jq -s .)

echo all_ok "$all_ok" 


echo '[preflight] building json' >&2

echo 'allRegistered' >&2
echo "$allRegistered" >&2

echo 'all_ok' >&2
echo "$all_ok" >&2

echo 'AKSCOMPUTEDEFAULT' >&2
echo "$AKSCOMPUTEDEFAULT" >&2

echo 'missing' >&2
echo "missing=${missing[*]}" >&2

echo 'present' >&2
echo "present=${present[*]}" >&2

echo 'missing_reg_json' >&2
echo "$missing_reg_json" >&2

echo 'gpu_quota_json' >&2
echo "$gpu_quota_json" >&2


jq -n \
  --argjson allRegistered "$( [[ "$allRegistered" == "true" ]] && echo true || echo false )" \
  --argjson allOk "$( [[ "$all_ok" == "true" ]] && echo true || echo false )" \
  --arg requiredVm "$AKSCOMPUTEDEFAULT" \
  --argjson missing "$(printf '%s\n' "${missing[@]:-}" | jq -R . | jq -s .)" \
  --argjson present "$(printf '%s\n' "${present[@]:-}" | jq -R . | jq -s .)" \
  --argjson missingRegister "${missing_reg_json:-[]}" \
  --argjson gpuQuota "${gpu_quota_json:-[]}" \
  '{
    allRegistered: $allRegistered,
    allOk: $allOk,
    missingRegister: $missingRegister,
    missing: $missing,
    present: $present,
    gpuQuota: $gpuQuota,
    requiredVm: $requiredVm
  }' > "$AZ_SCRIPTS_OUTPUT_PATH"

# Sanity check
echo 'checking output json validity' >&2

jq empty "$AZ_SCRIPTS_OUTPUT_PATH" || {
  echo '[preflight] ❌ Invalid JSON output, overwriting with {}' >&2
  echo '{}' > "$AZ_SCRIPTS_OUTPUT_PATH"
}


if [[ "$allRegistered" != "true" || "$all_ok" != "true" ]]; then
  echo "[preflight] ❌ Preflight checks failed" >&2
  exit 42
else
  echo "[preflight] ✅ Preflight checks passed" >&2
  exit 0
fi


# 1) set SUB_ID and rebuild the file with expansion (your previous file likely has a literal $SUB_ID)
trap 'echo "❌ failed at line $LINENO"; exit 1' ERR
[ -n "$SUB_ID" ] || { echo "❌ No SUB_ID"; exit 1; }
cat > aks-extensions-writer.json <<JSON
{
  "Name": "AKS ManagedCluster Extensions Writer",
  "IsCustom": true,
  "Description": "Can manage Microsoft.KubernetesConfiguration/extensions on AKS",
  "Actions": [
    "Microsoft.KubernetesConfiguration/extensions/read",
    "Microsoft.KubernetesConfiguration/extensions/write",
    "Microsoft.KubernetesConfiguration/extensions/delete"
  ],
  "NotActions": [],
  "DataActions": [],
  "NotDataActions": [],
  "AssignableScopes": [ "/subscriptions/$SUB_ID" ]
}
JSON

grep -q "/subscriptions/$SUB_ID" aks-extensions-writer.json  # aborts if missing (ERR trap)

# create OR update; both abort on error (ERR trap)
if az role definition list --name "AKS ManagedCluster Extensions Writer" --query "[].name" -o tsv | grep -q .; then
  az role definition update --role-definition aks-extensions-writer.json
else
  az role definition create --role-definition aks-extensions-writer.json
fi

# verify exact actions & scope; any mismatch aborts
az role definition list --name "AKS ManagedCluster Extensions Writer" --query "[0].permissions[0].actions[]" -o tsv | sort > /tmp/acts.txt
printf "%s\n" \
  "Microsoft.ContainerService/managedClusters/extensions/delete" \
  "Microsoft.ContainerService/managedClusters/extensions/read" \
  "Microsoft.ContainerService/managedClusters/extensions/write" | sort > /tmp/req.txt
diff -u /tmp/req.txt /tmp/acts.txt >/dev/null

az role definition list --name "AKS ManagedCluster Extensions Writer" --query "[0].assignableScopes[]" -o tsv | grep -qx "/subscriptions/$SUB_ID"

echo "✅ Custom role ensured & verified"

