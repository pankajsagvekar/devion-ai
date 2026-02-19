import re
from app.state import AgentState, BugMetadata

async def analyzer_agent(state: AgentState) -> AgentState:
    """Parses test outputs to extract bug metadata."""
    print("--- ANALYZER AGENT ---")
    
    if not state.current_test_results:
        return state

    output = state.current_test_results.output
    failures = []

    # Regex to extract file name, line number, and error message from pytest output
    # Example: F tests/test_math.py:5: AssertionError: 2 != 4
    pattern = r"F\s+(.*?):(\d+):\s+(.*)"
    matches = re.findall(pattern, output)

    for file_path, line, msg in matches:
        bug_type = "LOGIC"
        if "SyntaxError" in msg: bug_type = "SYNTAX"
        elif "ImportError" in msg: bug_type = "IMPORT"
        elif "IndentationError" in msg: bug_type = "INDENTATION"
        elif "TypeError" in msg: bug_type = "TYPE_ERROR"
        
        failures.append(BugMetadata(
            file_name=file_path,
            line_number=int(line),
            error_message=msg,
            bug_type=bug_type
        ))

    state.current_test_results.failures = failures
    return state
