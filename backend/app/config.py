import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
# This should be your frontend URL or a specific backend endpoint
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:8000/auth/callback")

# Execution Mode
USE_DOCKER = os.getenv("USE_DOCKER", "true").lower() == "true"

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    print("WARNING: GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not found.")
