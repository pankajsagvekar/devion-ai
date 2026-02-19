from app.state import AgentState, TestResult, BugMetadata
from app.services.docker_service import DockerService

async def test_runner_agent(state: AgentState) -> AgentState:
    """Executes tests in a Docker sandbox and captures output."""
    import re
    import os
    import asyncio
    from app.services.git_service import GitService
    from app.config import USE_DOCKER, GEMINI_API_KEY
    from google import genai

    print(f"--- TEST RUNNER AGENT (ITERATION {state.iteration}) ---")
    
    tester = DockerService()
    # First time? Clone and branch
    if not state.repo_path:
        git_svc = GitService()
        state.repo_path = git_svc.clone_repo(state.repository_url, state.team_name, state.github_token)
        git_svc.create_branch(state.repo_path, state.branch_name, state.github_token)

    # Run tests
    python_cmd = "python" if os.name == "nt" and not USE_DOCKER else "python3"
    cmd = "pytest --maxfail=5"
    if USE_DOCKER:
        test_output = tester.run_in_sandbox(state.repo_path, cmd)
    else:
        test_output = tester.run_local(state.repo_path, cmd)
    
    # Calculate preliminary failures from pytest
    is_system_error = any(msg in test_output.lower() for msg in [
        "cannot connect to the docker daemon", 
        "docker: command not found", 
        "permission denied", 
        "python was not found",
        "is not recognized as an internal or external command"
    ])
    pytest_failures = 1 if "failed" in test_output.lower() or "error" in test_output.lower() or is_system_error else 0
    
    # Fallback: If pytest found nothing or passed without errors, run a comprehensive sanity check
    if pytest_failures == 0:
        print("DEBUG: Pytest reported no failures. Running sanity check with compileall...")
        sanity_cmd = f"{python_cmd} -m compileall -q ."
        if USE_DOCKER:
            sanity_output = tester.run_in_sandbox(state.repo_path, sanity_cmd)
        else:
            sanity_output = tester.run_local(state.repo_path, sanity_cmd)
        
        if sanity_output.strip() and "python was not found" not in sanity_output.lower():
            print(f"DEBUG: Sanity check found potential issues: {len(sanity_output)} chars")
            test_output += "\n--- SANITY CHECK (COMPILEALL) ---\n" + sanity_output

        # NEW: Run Ruff for Linting (Mandatory hackathon requirement)
        print("DEBUG: Running Ruff for linting...")
        lint_cmd = "ruff check --output-format concise ."
        if USE_DOCKER:
            lint_output = tester.run_in_sandbox(state.repo_path, lint_cmd)
        else:
            lint_output = tester.run_local(state.repo_path, lint_cmd)
        
        # Check if we actually found linting errors (not just a command error)
        lint_found = any(re.match(r"(\S+):(\d+):(\d+):", line) for line in lint_output.splitlines())

        if lint_output.strip():
            print(f"DEBUG: Ruff output captured ({len(lint_output)} chars)")
            test_output += "\n--- LINTING CHECK (RUFF) ---\n" + lint_output

        # NEW: Final Fallback - AI Logic Auditor (Catch semantic bugs like the list-mutation error)
        if not lint_found:
            print("DEBUG: Performing AI Logic Audit (Final Fallback)...")
            
            async def run_ai_audit():
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    models_to_try = ["gemini-flash-latest", "gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-exp-1206"]
                    
                    files = [f for f in os.listdir(state.repo_path) if f.endswith('.py')]
                    for f_name in files:
                        with open(os.path.join(state.repo_path, f_name), 'r') as f:
                            code = f.read()
                        
                        audit_prompt = f"Analyze this Python code for LOGICAL BUGS or REDUNDANCY. If a logical bug is found, return EXACTLY: '[BUG]: {f_name}:line: message'. If the entire file is redundant, malicious, or should be removed, return EXACTLY: '[DELETE]: {f_name}: message'. If clean, return 'CLEAN'.\n\nCODE:\n{code}"
                        
                        audit_result = None
                        for model in models_to_try:
                            try:
                                response = client.models.generate_content(model=model, contents=audit_prompt)
                                audit_result = response.text
                                break
                            except Exception as e:
                                if "429" in str(e):
                                    print(f"DEBUG: Model {model} hit quota. Retrying in 20s with next model...")
                                    await asyncio.sleep(20)
                                    continue
                                print(f"DEBUG: AI Logic Audit failed for {model}: {e}")
                                continue

                        if audit_result and ("[BUG]:" in audit_result or "[DELETE]:" in audit_result):
                            print(f"DEBUG: AI Logic Auditor found a finding in {f_name}!")
                            return f"\n--- AI LOGIC AUDIT ---\n{audit_result.strip()}\n"
                    return ""
                except Exception as e:
                    print(f"DEBUG: AI Logic Audit outer error: {e}")
                    return ""

            # Run the async audit in the current loop
            audit_log = await run_ai_audit()
            test_output += audit_log

    print(f"DEBUG: Final Test Output Length: {len(test_output)}")
    print(f"DEBUG: Final Test Output (snippet):\n{test_output[:500]}")
    
    # Final failure calculation
    is_system_error = any(msg in test_output.lower() for msg in ["cannot connect to the docker daemon", "docker: command not found", "permission denied", "ruff: command not found"])
    
    # Check sections for actual bug markings
    has_lint_errors = "--- LINTING CHECK" in test_output and any(re.match(r"(\S+):(\d+):(\d+):", line) for line in test_output.splitlines())
    has_logic_errors = "--- AI LOGIC AUDIT ---" in test_output and ("[BUG]:" in test_output or "[DELETE]:" in test_output)
    
    total_failures = 1 if "failed" in test_output.lower() or "error" in test_output.lower() or "*** error compiling" in test_output.lower() or has_lint_errors or has_logic_errors or is_system_error else 0
    
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
