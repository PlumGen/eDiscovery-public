
# ---- App (rebuild on code changes only) ----
ARG BASE_IMAGE=consumerplumgenediscoveryregistry1f8c.azurecr.io/ediscovery-backend-base:1
FROM ${BASE_IMAGE}

# Install Tesseract OCR system package
#USER root

	

# Set SHELL so conda works for later RUNs and ENTRYPOINT
SHELL ["/bin/bash", "-c"]

# Set working directory
WORKDIR /app
COPY . .

# normalize line endings + make it executable
# (dos2unix might not be installed, so use sed fallback)
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Copy ADC key and set env var
#COPY key.json /app/key.json

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--stage", "extract"]
