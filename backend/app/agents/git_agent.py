from app.state import AgentState, CommitEntry
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
    
    # Build structured commit log entry from the latest failure
    failure = state.current_test_results.failures[0] if (state.current_test_results and state.current_test_results.failures) else None
    if failure:
        action_status = "DELETED" if failure.action == "DELETE" else "FIXED"
        commit_msg = f"[AI-AGENT] {last_fix}"
        entry = CommitEntry(
            file=failure.file_name,
            bug_type=failure.bug_type,
            line=failure.line_number,
            commit_message=commit_msg,
            status=action_status
        )
        state.commit_log.append(entry)
        print(f"DEBUG: Commit log entry added: {entry.model_dump()}")

    # Commit and push
    git_svc.commit_and_push(state.repo_path, state.branch_name, last_fix, state.github_token)
    state.commit_count += 1
    
    return state
