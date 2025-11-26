# Step 1: Build the React application
FROM node:20 AS build

WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./

RUN npm install

# Copy source code and remove any .env files
COPY frontend/ ./
RUN rm -f /app/.env /frontend/.env

# Build with Vite (assumes base: '/plumgen/' is set in vite.config.js)
RUN npm run build && ls -l /app/dist


# Step 2: Setup Python Backend + Nginx
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY ./frontendserver/requirements.txt /app/
RUN pip install --default-timeout=200 --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./frontendserver /app

# Make entrypoint executable
COPY ./frontendserver/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Install Nginx and Supervisor
RUN apt-get update && apt-get install -y nginx supervisor && rm -rf /var/lib/apt/lists/*


# Install Azure CLI
# RUN apt-get update && \
#     apt-get install -y curl apt-transport-https lsb-release gnupg && \
#     curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*


# Expose ports
EXPOSE 8080 5000

# Environment variables
ENV LOCAL=True
ENV VITE_API_URL=/api

# Remove default nginx site config
RUN rm -f /etc/nginx/sites-enabled/default

# ✅ Copy build output into correct subdirectory for /plumgen path
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist /usr/share/nginx/html/plumgen

# Copy NGINX config and Supervisor config
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start services
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
