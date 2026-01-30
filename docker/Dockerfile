FROM python:3.11-slim

# OCI Image Labels
LABEL org.opencontainers.image.title="Dockhand Guardian"
LABEL org.opencontainers.image.description="Docker sidecar watchdog service for automatic container recovery"
LABEL org.opencontainers.image.authors="Björn Strausmann"
LABEL org.opencontainers.image.url="https://github.com/strausmann/dockhand-guardian"
LABEL org.opencontainers.image.documentation="https://github.com/strausmann/dockhand-guardian#readme"
LABEL org.opencontainers.image.source="https://github.com/strausmann/dockhand-guardian"
LABEL org.opencontainers.image.licenses="MIT"
# Version, created, and revision are set dynamically during build via --build-arg

# Install curl for downloading docker-compose
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Docker Compose as a standalone binary
RUN curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install docker CLI binary
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-27.4.1.tgz -o docker.tgz && \
    tar -xzf docker.tgz --strip-components=1 -C /usr/local/bin docker/docker && \
    rm docker.tgz && \
    chmod +x /usr/local/bin/docker

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY ../pyproject.toml .
RUN pip install --no-cache-dir .

# Copy guardian script
COPY ../src/guardian.py .
RUN chmod +x guardian.py

# Set default environment variables
ENV MONITORED_CONTAINERS=dockhand-app,dockhand-database
ENV GRACE_SECONDS=300
ENV CHECK_INTERVAL=30
ENV COOLDOWN_SECONDS=600
ENV STACK_DIR=/stack
ENV MAINTENANCE_FILE=.maintenance

# Run guardian
CMD ["python", "guardian.py"]
