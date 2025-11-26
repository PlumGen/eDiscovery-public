#!/bin/sh

# Export all environment variables
export LOCAL=${LOCAL}
export RUNENV=${RUNENV}
export GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}

# Login to Azure with managed identity
# az login --identity

# az account show || {
#   echo "Azure login failed"
#   exit 1
# }

# Start Supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

