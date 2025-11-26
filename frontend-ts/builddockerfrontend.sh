#!/bin/bash



az acr login --name consumerplumgenediscoveryregistry1f8c

docker build --no-cache -t ediscovery-frontend-image . 
docker tag ediscovery-frontend-image consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-frontend-image
docker push consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-frontend-image	

 

az acr build --registry plumgenediscoverypublished --image ediscovery-frontend-image:latest .
