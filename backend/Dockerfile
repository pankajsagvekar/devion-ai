FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=production

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "app/main.py"]
