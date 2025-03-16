# Use Python Alpine base image
FROM --platform=$BUILDPLATFORM python:3.12-alpine

# Set environment variables
ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk add --no-cache curl

# Create and activate virtual environment
RUN python -m venv /venv

# Install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . . 

# Create a non-root user
RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /