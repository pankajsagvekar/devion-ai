import re
import os
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
        # Better classification based on keywords
        msg_lower = msg.lower()
        b_type = "LOGIC"
        if "syntax" in msg_lower or "expected" in msg_lower:
            b_type = "SYNTAX"
        elif "indentation" in msg_lower or "tab" in msg_lower:
            b_type = "INDENTATION"
        elif "import" in msg_lower or "nameerror" in msg_lower:
            b_type = "IMPORT"
        elif "typeerror" in msg_lower:
            b_type = "TYPE_ERROR"
        elif "unused" in msg_lower or "line too long" in msg_lower:
            b_type = "LINTING"

        failures.append(BugMetadata(
            file_name=file_path.strip(),
            line_number=int(line),
            error_message=msg.strip(),
            bug_type=b_type
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

    # Pattern 4: Ruff Linting (demo_error.py:5:1: F401 [*] message)
    pattern4 = r"(\S+):(\d+):(\d+):\s+(\w+)\s+(.*)"
    matches4 = re.findall(pattern4, output)
    print(f"DEBUG: Pattern 4 (Ruff) found {len(matches4)} matches")
    for file_path, line, col, code, msg in matches4:
        failures.append(BugMetadata(
            file_name=file_path.strip(),
            line_number=int(line),
            error_message=f"[{code}] {msg.strip()}",
            bug_type="LINTING"
        ))

    # Pattern 5: AI Logic Auditor ([BUG]: demo_error.py:5: message)
    pattern5 = r"\[BUG\]:\s+(\S+):(\d+):\s+(.*)"
    matches5 = re.findall(pattern5, output)
    print(f"DEBUG: Pattern 5 (AI Logic) found {len(matches5)} matches")
    for file_path, line, msg in matches5:
        failures.append(BugMetadata(
            file_name=file_path.strip(),
            line_number=int(line),
            error_message=f"[AI-AUDIT] {msg.strip()}",
            bug_type="LOGIC",
            action="FIX"
        ))

    # Pattern 6: AI Logic Auditor Deletion ([DELETE]: file_name: message)
    pattern6 = r"\[DELETE\]:\s+(\S+):\s+(.*)"
    matches6 = re.findall(pattern6, output)
    print(f"DEBUG: Pattern 6 (AI Delete) found {len(matches6)} matches")
    for file_path, msg in matches6:
        failures.append(BugMetadata(
            file_name=file_path.strip(),
            line_number=1,
            error_message=f"[AI-DELETE] {msg.strip()}",
            bug_type="LOGIC",
            action="DELETE"
        ))

    if not failures and state.current_test_results.total_failures > 0:
        # Fallback for unrecognized errors (System Errors)
        target_file = "main.py"
        if state.repo_path and os.path.exists(state.repo_path):
            py_files = [f for f in os.listdir(state.repo_path) if f.endswith('.py')]
            if py_files:
                target_file = py_files[0]

        failures.append(BugMetadata(
            file_name=target_file,
            line_number=1,
            error_message="Agent detected a potential issue but could not pinpoint the exact line. Please perform a full logic audit.",
            bug_type="LOGIC"
        ))

    state.current_test_results.failures = failures
    print(f"DEBUG: Analyzer identified {len(failures)} failures total")
    return state
