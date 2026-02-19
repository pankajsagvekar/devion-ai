FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-install common testing and quality dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-json-report \
    pytest-asyncio \
    requests \
    httpx \
    ruff \
    flake8 \
    mypy

# Standardize working directory for the sandbox
WORKDIR /app

# The agent will mount the repository to /app at runtime
CMD ["pytest", "--json-report", "--json-report-file=report.json"]
