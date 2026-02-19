#!/bin/bash

# Build the sandbox image
echo "Building Devion AI Sandbox image..."
docker build -t devion-sandbox -f backend/sandbox.Dockerfile backend/

echo "Build complete. You can now run the agent."
