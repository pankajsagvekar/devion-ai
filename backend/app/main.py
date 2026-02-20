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
from app.config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_REDIRECT_URI, FRONTEND_URL, ENVIRONMENT

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
        redirect_url = f"{FRONTEND_URL}/?token={token_data['access_token']}"
        if not os.getenv("FRONTEND_URL") and ENVIRONMENT == "production":
             print("CRITICAL: FRONTEND_URL not set in production! Defaults to localhost.")
        
        return RedirectResponse(redirect_url)

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

    # Fast-fail for missing critical config
    from app.config import GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Backend misconfigured: GEMINI_API_KEY missing.")
    if not request.github_token:
        raise HTTPException(status_code=400, detail="Authentication required: No GitHub token provided.")

    try:
        graph = create_graph()
        
        # Run the workflow
        print(f"DEBUG: Starting agent run for {request.team_name} (Branch: {branch_name})")
        final_output = await graph.ainvoke(initial_state)
        
        # Build response: results_json fields + commit_log
        results = final_output.get("results_json", {})
        if not results:
             print("WARNING: Agent finished but 'results_json' is empty.")
             # Fallback payload to prevent frontend crash
             results = {
                 "final_status": "FAILED",
                 "total_failures": 0,
                 "total_fixes": 0,
                 "iterations_used": 0,
                 "score_calculation": {"final_score": 0}
             }

        response = dict(results)
        response["commit_log"] = [entry.model_dump() for entry in final_output.get("commit_log", [])]
        return response
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: Agent crash during execution:\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Agent internal failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable for Render/production compatibility
    port = int(os.getenv("PORT", 8000))
    # Enable reload=True ONLY in development
    is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=is_dev)
