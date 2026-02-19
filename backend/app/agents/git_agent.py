from app.state import AgentState
from app.services.git_service import GitService

async def git_agent(state: AgentState) -> AgentState:
    """Handles commits and pushes."""
    print("--- GIT AGENT ---")
    
    if not state.fixes_applied:
        return state

    git_svc = GitService()
    last_fix = state.fixes_applied[-1]
    
    # Commit and push
    git_svc.commit_and_push(state.repo_path, state.branch_name, last_fix, state.github_token)
    state.commit_count += 1
    
    return state
