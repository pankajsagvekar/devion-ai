import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.state import AgentState, TestResult
from app.graph import create_graph

app = FastAPI(title="Autonomous CI/CD Healing Agent")

class RunRequest(BaseModel):
    repository_url: str
    team_name: str
    leader_name: str

@app.post("/run-agent")
async def run_agent(request: RunRequest):
    # Sanitize team/leader names for branch creation
    clean_team = request.team_name.upper().replace(" ", "_")
    clean_leader = request.leader_name.upper().replace(" ", "_")
    branch_name = f"{clean_team}_{clean_leader}_AI_FIX"

    initial_state = AgentState(
        repository_url=request.repository_url,
        team_name=request.team_name,
        leader_name=request.leader_name,
        branch_name=branch_name,
        start_time=time.time()
    )

    graph = create_graph()
    
    # Run the workflow
    # Note: In a real prod environment, this should be async/backgrounded
    final_output = await graph.ainvoke(initial_state)
    
    return final_output["results_json"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
