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
        state.repo_path = git_svc.clone_repo(state.repository_url, state.team_name)
        git_svc.create_branch(state.repo_path, state.branch_name)

    # Run tests
    test_output = tester.run_in_sandbox(state.repo_path, "pytest --maxfail=5")
    
    # Crude parsing for now - normally analyzer handles this, but we need to know if it passed
    total_failures = 1 if "failed" in test_output.lower() or "error" in test_output.lower() else 0
    if "passed" in test_output.lower() and total_failures == 0:
        total_failures = 0

    state.current_test_results = TestResult(
        total_failures=total_failures,
        output=test_output
    )
    
    return state
