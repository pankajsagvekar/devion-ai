FROM python:3.10-slim

# Install system dependencies (git might be needed if tests run git commands)
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pre-install common testing dependencies
RUN pip install \
    pytest \
    pytest-json-report \
    requests \
    pytest-asyncio

# Standardize working directory for the sandbox
WORKDIR /app

# The agent will mount the repository to /app at runtime
CMD ["pytest", "--json-report", "--json-report-file=report.json"]
