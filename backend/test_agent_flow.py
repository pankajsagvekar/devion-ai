import requests
import json
import os
import sys
from dotenv import load_dotenv

def trigger_agent():
    load_dotenv()
    
    # Configuration
    # Use the API URL from environment or fallback to localhost for local testing
    base_url = os.getenv("VITE_API_URL", "http://localhost:8000")
    url = f"{base_url}/run-agent"
    
    token = os.getenv("GITHUB_TOKEN") or input("Enter your GitHub token: ").strip()
    repo_url = os.getenv("TEST_REPO_URL") or input("Enter your repo URL (e.g., https://github.com/user/repo): ").strip()
    team_name = input("Enter Team Name (e.g. YOYO): ").strip() or "YOYO"
    team_leader = input("Enter Team Leader (e.g. HELLO): ").strip() or "HELLO"

    payload = {
        "repository_url": repo_url,
        "team_name": team_name,
        "team_leader": team_leader,
        "github_token": token
    }

    print(f"\n--- TRIGGERING AGENT AT {url} ---")
    print(f"Target Repo: {repo_url}")
    print(f"Team: {team_name} (Leader: {team_leader})")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("\nSUCCESS: Agent started successfully!")
            print("Response:", json.dumps(response.json(), indent=2))
            print("\nNOW: Check your backend terminal logs to see the agent work in real-time.")
        else:
            print(f"\nFAILED: Server returned {response.status_code}")
            print("Error Details:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server. Is 'python3 backend/app/main.py' running?")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    trigger_agent()
