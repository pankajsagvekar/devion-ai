from app.state import AgentState
from app.services.git_service import GitService

async def git_agent(state: AgentState) -> AgentState:
    """Handles commits and pushes."""
    print("--- GIT AGENT ---")
    
    if not state.fixes_applied:
        print("DEBUG: Git Agent skipping - no fixes applied yet.")
        return state

    print(f"DEBUG: Git Agent starting commit/push for {len(state.fixes_applied)} fixes.")
    git_svc = GitService()
    last_fix = state.fixes_applied[-1]
    
    # Commit and push
    git_svc.commit_and_push(state.repo_path, state.branch_name, last_fix, state.github_token)
    state.commit_count += 1
    
    return state
