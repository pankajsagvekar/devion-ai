FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements or just install needed packages
RUN pip install \
    fastapi \
    uvicorn \
    langgraph \
    pydantic \
    gitpython \
    pytest \
    pytest-json-report \
    httpx

# Copy backend code
COPY ./backend /app/backend

# Set environment variables
ENV PYTHONPATH=/app/backend

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "backend/app/main.py"]
