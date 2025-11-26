#!/bin/bash
# 1) build/push base once
docker build -f Dockerfile.base -t consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-base:1 .
docker push consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-base:1