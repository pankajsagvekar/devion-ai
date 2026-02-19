from app.state import AgentState

async def orchestrator_agent(state: AgentState) -> AgentState:
    """Controls the retry loop and determines if processing should continue."""
    print(f"--- ORCHESTRATOR ITERATION {state.iteration} ---")
    
    # Simple increment: Orchestrator is responsible for tracking iterations
    state.iteration += 1
    
    # Initialize branch_name if missing
    if not state.branch_name:
        state.branch_name = f"{state.team_name}_{state.leader_name}_AI_Fix"
        print(f"DEBUG: Initialized branch name to {state.branch_name}")

    if state.final_status in ["PASSED", "FAILED"]:
        return state

    return state
