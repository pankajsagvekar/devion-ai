import re
from app.state import AgentState, BugMetadata

async def analyzer_agent(state: AgentState) -> AgentState:
    """Parses test outputs to extract bug metadata."""
    print("--- ANALYZER AGENT ---")
    
    if not state.current_test_results:
        return state

    output = state.current_test_results.output
    failures = []

    print(f"DEBUG: Analyzer processing output of length {len(output)}")
    
    # Improved patterns to capture more pytest failure formats
    # Pattern 1: F tests/test_math.py:5: AssertionError
    pattern1 = r"F\s+(.*?):(\d+):\s+(.*)"
    # Pattern 2: _________________ test_error _________________
    #            tests/test_math.py:5: in test_error
    pattern2 = r"(\S+):(\d+): in \S+"
    
    matches1 = re.findall(pattern1, output)
    print(f"DEBUG: Pattern 1 found {len(matches1)} matches")
    
    for file_path, line, msg in matches1:
        failures.append(BugMetadata(
            file_name=file_path.strip(),
            line_number=int(line),
            error_message=msg.strip(),
            bug_type="LOGIC" # Default, can be refined
        ))

    if not failures:
        # Pattern 3: *** Error compiling './demo_error.py'...
        #            File "./demo_error.py", line 6
        pattern3 = r"\*\*\* Error compiling '(.*?)'.*?\n\s+File \".*?\", line (\d+)"
        matches3 = re.findall(pattern3, output, re.DOTALL)
        print(f"DEBUG: Pattern 3 found {len(matches3)} matches")
        for file_path, line in matches3:
            failures.append(BugMetadata(
                file_name=file_path.replace("./", ""),
                line_number=int(line),
                error_message="SyntaxError identified by compileall",
                bug_type="SYNTAX"
            ))

    state.current_test_results.failures = failures
    print(f"DEBUG: Analyzer identified {len(failures)} failures total")
    return state
