from app.state import AgentState, TestResult, BugMetadata
from app.services.docker_service import DockerService

async def test_runner_agent(state: AgentState) -> AgentState:
    """Executes tests in a Docker sandbox and captures output."""
    print(f"--- TEST RUNNER AGENT (ITERATION {state.iteration}) ---")
    
    tester = DockerService()
    # First time? Clone and branch
    if not state.repo_path:
        from app.services.git_service import GitService
        git_svc = GitService()
        state.repo_path = git_svc.clone_repo(state.repository_url, state.team_name, state.github_token)
        git_svc.create_branch(state.repo_path, state.branch_name, state.github_token)

    # Run tests
    from app.config import USE_DOCKER
    cmd = "pytest --maxfail=5"
    if USE_DOCKER:
        test_output = tester.run_in_sandbox(state.repo_path, cmd)
    else:
        test_output = tester.run_local(state.repo_path, cmd)
    
    # Calculate preliminary failures from pytest
    is_system_error = any(msg in test_output.lower() for msg in ["cannot connect to the docker daemon", "docker: command not found", "permission denied"])
    pytest_failures = 1 if "failed" in test_output.lower() or "error" in test_output.lower() or is_system_error else 0
    
    # Fallback: If pytest found nothing or passed without errors, run a comprehensive sanity check
    if pytest_failures == 0:
        print("DEBUG: Pytest reported no failures. Running sanity check with compileall...")
        sanity_cmd = "python3 -m compileall -q ."
        if USE_DOCKER:
            sanity_output = tester.run_in_sandbox(state.repo_path, sanity_cmd)
        else:
            sanity_output = tester.run_local(state.repo_path, sanity_cmd)
        
        if sanity_output.strip():
            print(f"DEBUG: Sanity check found potential issues: {len(sanity_output)} chars")
            test_output += "\n--- SANITY CHECK (COMPILEALL) ---\n" + sanity_output

    print(f"DEBUG: Final Test Output Length: {len(test_output)}")
    print(f"DEBUG: Final Test Output (snippet):\n{test_output[:500]}")
    
    # Final failure calculation
    is_system_error = any(msg in test_output.lower() for msg in ["cannot connect to the docker daemon", "docker: command not found", "permission denied"])
    total_failures = 1 if "failed" in test_output.lower() or "error" in test_output.lower() or "*** error compiling" in test_output.lower() or is_system_error else 0
    
    if is_system_error:
        print("CRITICAL: Detected System/Docker error in test runner!")
    
    print(f"DEBUG: Final calculated total_failures: {total_failures}")
    
    if "passed" in test_output.lower() and total_failures == 0 and not is_system_error:
        total_failures = 0

    state.current_test_results = TestResult(
        total_failures=total_failures,
        output=test_output
    )
    
    return state
