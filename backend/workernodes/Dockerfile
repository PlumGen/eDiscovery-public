FROM rapidsai/base:24.10a-cuda12.2-py3.10

# Use root to set up the environment
USER root

# Copy environment files early
COPY conda_explicit.txt .
COPY clean_requirements.txt .

# Recreate environment safely from explicit spec
RUN conda create --name rapids_clean --file conda_explicit.txt && \
    conda clean -afy

# Activate env and install pip requirements
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate rapids_clean && \
    pip install --default-timeout=120 --retries=10 --no-cache-dir -r clean_requirements.txt && \
    python -m spacy download en_core_web_md"

#	&& \
#	python -m nltk.downloader stopwords && \
#	python -m nltk.downloader wordnet && \
#	python -m nltk.downloader punkt"



# Set SHELL so conda works for later RUNs and ENTRYPOINT
SHELL ["/bin/bash", "-c"]

# Set working directory
WORKDIR /app
COPY . .

RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate rapids_clean && \
	python download_model.py"
	

# normalize line endings + make it executable
# (dos2unix might not be installed, so use sed fallback)
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Copy ADC key and set env var
COPY key.json /app/key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/key.json
ENV PYTHONUNBUFFERED=1

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--stage", "extract"]


#docker build --no-cache -t ediscovery-backend-gpu-image .
#docker run --rm ediscovery-backend-gpu-image --stage extract

