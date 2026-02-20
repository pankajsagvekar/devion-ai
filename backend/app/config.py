import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# GitHub OAuth Configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
# The redirect URI must match your GitHub OAuth App settings exactly
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
# The frontend URL for the final OAuth redirect
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080")

# Execution Mode
USE_DOCKER = os.getenv("USE_DOCKER", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if not GEMINI_API_KEY:
    print("CRITICAL: GEMINI_API_KEY not found in environment variables.")

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    print("CRITICAL: GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not found.")

if ENVIRONMENT == "production" and not GITHUB_REDIRECT_URI:
    print("CRITICAL: GITHUB_REDIRECT_URI must be set in production!")
