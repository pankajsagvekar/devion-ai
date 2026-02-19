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

    # 1. Run Pytest
    cmd = "pytest --maxfail=5"
    if USE_DOCKER:
        test_output = tester.run_in_sandbox(state.repo_path, cmd)
    else:
        test_output = tester.run_local(state.repo_path, cmd)
    
    # 2. Run Compileall (Sanity Check)
    print("DEBUG: Running sanity check with compileall...")
    sanity_cmd = "python3 -m compileall -q ."
    if USE_DOCKER:
        sanity_output = tester.run_in_sandbox(state.repo_path, sanity_cmd)
    else:
        sanity_output = tester.run_local(state.repo_path, sanity_cmd)
    
    if sanity_output.strip():
        print(f"DEBUG: Sanity check found potential issues: {len(sanity_output)} chars")
        test_output += "\n--- SANITY CHECK (COMPILEALL) ---\n" + sanity_output

    # 3. Run Ruff for Linting
    print("DEBUG: Running Ruff for linting...")
    lint_cmd = "ruff check --output-format concise ."
    if USE_DOCKER:
        lint_output = tester.run_in_sandbox(state.repo_path, lint_cmd)
    else:
        lint_output = tester.run_local(state.repo_path, lint_cmd)
    
    if lint_output.strip():
        print(f"DEBUG: Ruff output captured ({len(lint_output)} chars)")
        test_output += "\n--- LINTING CHECK (RUFF) ---\n" + lint_output

    # 4. Run AI Logic Auditor (Comprehensive Sweep)
    print("DEBUG: Performing AI Logic Audit (Parallel)...")
    from app.utils.ai_utils import call_ai
    
    async def run_ai_audit():
        # Optimization: If standard tests or linters already failed, skip the expensive AI logic sweep for this iteration
        has_lint_errors = "--- LINTING CHECK" in test_output and any(re.match(r"(\S+):(\d+):(\d+):", line) for line in test_output.splitlines())
        has_test_failures = "failed" in test_output.lower() or "error" in test_output.lower() or "*** error compiling" in test_output.lower()
        
        if has_test_failures or has_lint_errors:
            print("DEBUG: Bypassing AI Logic Audit because standard tests/linters already found failures (speed optimization).")
            return ""
            
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            files = [f for f in os.listdir(state.repo_path) if f.endswith('.py')]
            if not files:
                return ""
                
            code_contexts = []
            for f_name in files:
                try:
                    with open(os.path.join(state.repo_path, f_name), 'r') as f:
                        code = f.read()
                    code_contexts.append(f"--- FILE: {f_name} ---\n{code}")
                except Exception as e:
                    print(f"DEBUG: Could not read {f_name} for audit: {e}")
                    
            combined_code = "\n".join(code_contexts)
            
            audit_prompt = f"Analyze these Python files for LOGICAL BUGS or REDUNDANCY. If a logical bug is found, return EXACTLY: '[BUG]: filename:line: message'. If an entire file is redundant or harmful, return EXACTLY: '[DELETE]: filename: message'. Do not return anything else.\n\nFILES:\n{combined_code}"
            
            result = await call_ai(client, audit_prompt)
            if result and ("[BUG]:" in result or "[DELETE]:" in result):
                return f"\n--- AI LOGIC AUDIT ---\n{result}\n"
            return ""
        except Exception as e:
            print(f"DEBUG: AI Logic Audit outer error: {e}")
            return ""

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
