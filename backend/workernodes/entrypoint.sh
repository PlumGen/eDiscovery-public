#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate rapids_clean
chmod +x ./licenseCheck.bin
exec python localcontroller.py "$@" 2>&1
