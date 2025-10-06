#!/bin/bash
# 2) build app fast on code changes
# docker build -f Dockerfile.app \
#   --build-arg BASE_IMAGE=plumgenediscoveryregistry.azurecr.io/ediscovery-backend-base:1 \
#   -t plumgenediscoveryregistry.azurecr.io/ediscovery-backend-gpu-image:latest .
# docker push plumgenediscoveryregistry.azurecr.io/ediscovery-backend-gpu-image:latest


az acr login --name plumgenediscoverypublished
az acr build -r plumgenediscoverypublished -f Dockerfile.app -t plumgenediscoverypublished.azurecr.io/ediscovery-backend-gpu-image:latest .