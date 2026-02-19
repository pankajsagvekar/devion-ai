from app.state import AgentState
from app.services.git_service import GitService

async def git_agent(state: AgentState) -> AgentState:
    """Handles the final commit and push after all fixes are applied."""
    print("--- GIT AGENT (FINAL COMMIT) ---")
    
    if not state.fixes_applied:
        print("DEBUG: Git Agent skipping - no fixes applied during this run.")
        return state

    print(f"DEBUG: Git Agent starting final commit/push for {len(state.fixes_applied)} applied fixes.")
    git_svc = GitService()
    
    # Unified commit message for all fixes iteration
    final_commit_msg = f"[AI-AGENT] Healing repository: Applied {len(state.fixes_applied)} fixes/pruning operations."
    
    # Commit and push everything at once
    try:
        git_svc.commit_and_push(state.repo_path, state.branch_name, final_commit_msg, state.github_token)
        state.commit_count = 1  # We only did one final commit
        print(f"SUCCESS: Final consolidated commit pushed: {final_commit_msg}")
    except Exception as e:
        print(f"ERROR during final Git operation: {e}")
        state.final_status = "GIT_ERROR"
    
    return state
