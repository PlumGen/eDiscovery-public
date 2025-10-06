#!/bin/bash



az acr login --name plumgenediscoverypublished

docker build --no-cache -t ediscovery-frontend-image .
docker tag ediscovery-frontend-image plumgenediscoverypublished.azurecr.io/ediscovery-frontend-image
docker push plumgenediscoverypublished.azurecr.io/ediscovery-frontend-image	



az acr build --registry plumgenediscoverypublished --image ediscovery-frontend-image:latest .
