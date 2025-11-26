#!/bin/bash
# 2) build app fast on code changes
# docker build -f Dockerfile.app \
#   --build-arg BASE_IMAGE=plumgenediscoveryregistry.azurecr.io/ediscovery-backend-base:1 \
#   -t plumgenediscoveryregistry.azurecr.io/ediscovery-backend-gpu-image:latest .
# docker push plumgenediscoveryregistry.azurecr.io/ediscovery-backend-gpu-image:latest


az acr login --name consumerplumgenediscoveryregistry1f8c
az acr build -r consumerplumgenediscoveryregistry1f8c -f Dockerfile.app -t consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-gpu-image:latest .

docker build -f Dockerfile.app -t consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-gpu-image:latest .
docker push consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-gpu-image:latest
