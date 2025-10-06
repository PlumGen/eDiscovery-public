#!/bin/bash
# 1) build/push base once
docker build -f Dockerfile.base -t plumgenediscoverypublished.azurecr.io/ediscovery-backend-base:1 .
docker push plumgenediscoverypublished.azurecr.io/ediscovery-backend-base:1