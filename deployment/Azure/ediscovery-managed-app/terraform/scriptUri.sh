#!/usr/bin/env bash
set -Eeuo pipefail
set -x
trap 'rc=$?; echo "ERROR line $LINENO exit $rc" >&2; exit $rc' ERR
: "${AZ_SCRIPTS_OUTPUT_PATH:?missing}"

echo "[script] starting…"



: "${DB_ADMIN_PASSWORD:?DB_ADMIN_PASSWORD not set}"
: "${PUBLISHER_USERNAME:?PUBLISHER_USERNAME not set}"
: "${PUBLISHER_PASSWORD:?PUBLISHER_PASSWORD not set}"

# Terraform automation env
export TF_IN_AUTOMATION=1
export TF_INPUT=0
export TF_LOG=ERROR



# ... proceed with terraform work ...

# --- preflight: tools & helpers (no sudo) ---
SUDO=""
if command -v sudo >/dev/null 2>&1; then SUDO="sudo"; fi

have() { command -v "$1" >/dev/null 2>&1; }

# downloader
fetch() {
  src="$1"; dst="$2"
  if have curl; then curl -fsSL -o "$dst" "$src"
  elif have wget; then wget -q -O "$dst" "$src"
  else
    python3 - "$src" "$dst" <<'PY'
import sys, urllib.request
urllib.request.urlretrieve(sys.argv[1], sys.argv[2])
PY
  fi
}

# unzipper
unzip_to() {
  z="$1"; dir="$2"
  if have unzip; then unzip -q "$z" -d "$dir"
  else
    python3 - "$z" "$dir" <<'PY'
import sys, zipfile, os
z, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
with zipfile.ZipFile(z) as zf:
    zf.extractall(out)
PY
  fi
}

# try to install curl/unzip only if package manager exists (works when running as root)
if ! have curl && have apt-get; then $SUDO apt-get update -y && $SUDO apt-get install -y curl
elif ! have curl && have yum; then $SUDO yum install -y curl
elif ! have curl && have apk; then $SUDO apk add --no-cache curl
fi
if ! have unzip && have apt-get; then $SUDO apt-get update -y && $SUDO apt-get install -y unzip
elif ! have unzip && have yum; then $SUDO yum install -y unzip
elif ! have unzip && have apk; then $SUDO apk add --no-cache unzip
fi




# normalize PKG_BASE to end with '/'
case "${PKG_BASE:-}" in */) :;; *) PKG_BASE="${PKG_BASE}/";; esac
echo "PKG_BASE=${PKG_BASE}"

TFV="${TFV:-1.7.5}"

WORK="/work"
BIN="${WORK}/bin"
TF_DIR="${WORK}/terraform"
mkdir -p "${WORK}" "${BIN}" "${TF_DIR}"
export PATH="${BIN}:${PATH}"

# 1) Install Terraform into ${BIN}
fetch "https://releases.hashicorp.com/terraform/${TFV}/terraform_${TFV}_linux_amd64.zip" /tmp/tf.zip
unzip_to /tmp/tf.zip "${BIN}"
chmod +x "${BIN}/terraform"

# 2) Bring Terraform sources
echo "Fetching terraform bundle: ${TF_ZIP_URI}"
fetch "${TF_ZIP_URI}" /tmp/tfpkg.zip

# Unpack into /tmp/unpack
rm -rf /tmp/unpack
mkdir -p /tmp/unpack
unzip_to  /tmp/tfpkg.zip /tmp/unpack

echo "---- tree under /tmp/unpack (depth 3) ----"
find /tmp/unpack -maxdepth 3 -type f -print

# your mv logic
# Detect bundle structure
top_dirs=($(find /tmp/unpack -mindepth 1 -maxdepth 1 -type d))
top_files=($(find /tmp/unpack -mindepth 1 -maxdepth 1 -type f))

if [[ ${#top_dirs[@]} -eq 1 && ${#top_files[@]} -eq 0 ]]; then
  echo "[script] Detected single top-level folder, flattening..."
  mv /tmp/unpack/*/* "${TF_DIR}/"
else
  echo "[script] Detected multiple top-level entries, moving as-is..."
  mv /tmp/unpack/* "${TF_DIR}/"
fi

# Validation
echo "[script] Validating Terraform sources under ${TF_DIR}..."
if find "${TF_DIR}" -type f -name '*.tf' -quit >/dev/null; then
  echo "[script] Found Terraform files:"
  find "${TF_DIR}" -maxdepth 3 -type f -name '*.tf'
else
  echo "ERROR: No .tf files found under ${TF_DIR}"
  printf '{"status":"error","reason":"no_tf_files"}' > "$AZ_SCRIPTS_OUTPUT_PATH"
  exit 1
fi


echo "---- tree under ${TF_DIR} (depth 3) ----"
find "${TF_DIR}" -maxdepth 3 -type f -print



# 3) Azure auth (UAMI)
az login --identity --allow-no-subscriptions >/dev/null
az account set -s "${SUBSCRIPTION_ID}"

# 4) Terraform env
export ARM_USE_MSI="${ARM_USE_MSI}"
export ARM_SUBSCRIPTION_ID="${ARM_SUBSCRIPTION_ID}"
export ARM_TENANT_ID="${ARM_TENANT_ID}"
export ARM_CLIENT_ID="${ARM_CLIENT_ID}"


export TF_VAR_subscription_id="${SUBSCRIPTION_ID}"
export TF_VAR_tenant_id="${TENANT_ID}"
export TF_VAR_name="${MANAGED_RG_NAME}"
export TF_VAR_resource_location="${LOCATION}"
export TF_VAR_resource_group_name="${MANAGED_RG_NAME}"
export TF_VAR_allowed_ip_ranges="${ALLOWED_IP_RANGES}"
export TF_VAR_db_admin_password="${DB_ADMIN_PASSWORD}"
export TF_VAR_publisher_username="${PUBLISHER_USERNAME}"
export TF_VAR_publisher_password="${PUBLISHER_PASSWORD}"

export TF_VAR_aks_compute_default="${AKSCOMPUTEDEFAULT}"
export TF_VAR_aks_compute_cpu="${AKSCOMPUTECPU}"
export TF_VAR_aks_compute_gpu="${AKSCOMPUTEGPU}"  

export TF_VAR_vpn_server_app_id="${VPNSERVERAPPID}"  
export TF_VAR_frontend_aad_client_id="${FRONTENDAADCLIENTID}"  
export TF_VAR_frontend_aad_client_secret="${FRONTENDAADCLIENTSECRET}"  

export TF_VAR_hostname="${HOST}"
export TF_VAR_hostname_path="${HOSTPATH}"  

cd "${TF_DIR}"
terraform init -input=false -upgrade -no-color


if [[ -f static_env_vars.tfvars.json ]]; then
  terraform apply -auto-approve -input=false -no-color -lock-timeout=10m -var-file="static_env_vars.tfvars.json"
else
  terraform apply -auto-approve -input=false -no-color -lock-timeout=10m
fi

# Write script output so ARM doesn't show a generic failure
# Prefer returning TF outputs if defined; otherwise return a simple OK
if terraform output -json >/tmp/tfout.json 2>/dev/null; then
  cat /tmp/tfout.json > "$AZ_SCRIPTS_OUTPUT_PATH"
else
  printf '{"status":"ok","tf_dir":"%s"}' "$TF_DIR" > "$AZ_SCRIPTS_OUTPUT_PATH"
fi



az group update --name "${MANAGED_RG_NAME}" --set tags.Application="plumgenediscovery-${MANAGED_RG_NAME}" 


exit 0