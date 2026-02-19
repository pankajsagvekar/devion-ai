from app.state import AgentState

async def orchestrator_agent(state: AgentState) -> AgentState:
    """Controls the retry loop and determines if processing should continue."""
    print(f"--- ORCHESTRATOR ITERATION {state.iteration} ---")
    
    # Simple increment: Orchestrator is responsible for tracking iterations
    state.iteration += 1
    
    # If final results are already set (from a previous termination), just return
    if state.final_status in ["PASSED", "FAILED"]:
        return state

    return state
