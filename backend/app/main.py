import sys
import os
import httpx
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Auto-inject venv bin/Scripts into PATH for local execution stability
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
venv_dirs = [os.path.join(root_dir, "venv", "Scripts"), os.path.join(root_dir, "venv", "bin")]
for venv_bin in venv_dirs:
    if os.path.exists(venv_bin) and venv_bin not in os.environ["PATH"]:
        os.environ["PATH"] = venv_bin + os.pathsep + os.environ["PATH"]
        print(f"DEBUG: Injected venv path: {venv_bin}")

from app.state import AgentState, TestResult
from app.graph import create_graph
from app.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI

app = FastAPI(title="Autonomous CI/CD Healing Agent")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for hackathon simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "debug", "time": time.time()}

# OAuth Endpoints
@app.get("/auth/login")
async def login_github():
    """Redirects the user to GitHub for authentication."""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GITHUB_CLIENT_ID not configured")
    
    scope = "repo" # Required to clone and push
    url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={GITHUB_REDIRECT_URI}&scope={scope}"
    return RedirectResponse(url)

@app.get("/auth/callback")
async def auth_callback(code: str = Query(None)):
    """Exchanges GitHub authorization code for an access token."""
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI
            }
        )
        
        token_data = response.json()
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail=f"Failed to get token: {token_data.get('error_description', 'Unknown error')}")
            
        # Redirect back to frontend with the token
        frontend_url = "http://localhost:8080" # Update this for production
        return RedirectResponse(f"{frontend_url}/?token={token_data['access_token']}")

class RunRequest(BaseModel):
    repository_url: str
    github_token: str
    team_name: str
    team_leader: str

@app.post("/run-agent")
async def run_agent(request: RunRequest):
    import re
    # Sanitize team/leader names for branch creation
    clean_team = re.sub(r'[^a-zA-Z0-9_]', '', request.team_name.replace(" ", "_").upper())
    clean_leader = re.sub(r'[^a-zA-Z0-9_]', '', request.team_leader.replace(" ", "_").upper())
    branch_name = f"{clean_team}_{clean_leader}_AI_Fix"

    initial_state = AgentState(
        repository_url=request.repository_url,
        team_name=request.team_name,
        leader_name=request.team_leader,
        github_token=request.github_token,
        branch_name=branch_name,
        start_time=time.time()
    )

    graph = create_graph()
    
    # Run the workflow
    # Note: In a real prod environment, this should be async/backgrounded
    final_output = await graph.ainvoke(initial_state)
    
    # Build response: results_json fields + commit_log (not saved to results.json on disk)
    response = dict(final_output["results_json"])
    response["commit_log"] = [entry.model_dump() for entry in final_output.get("commit_log", [])]
    return response

if __name__ == "__main__":
    import uvicorn
    # Enable reload=True for development to pick up changes automatically
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
