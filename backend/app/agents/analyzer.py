import re
import os
import json
from google import genai
from app.state import AgentState, BugMetadata
from app.config import GEMINI_API_KEY
from app.utils.ai_utils import call_ai, extract_json

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



    if not failures and state.current_test_results.total_failures > 0:
        print("INFO: Regex parsing failed to find specific failures. Falling back to LLM-based analysis.")
        
        if not GEMINI_API_KEY:
            print("ERROR: GEMINI_API_KEY is not set. Cannot use LLM fallback.")
        else:
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                
                prompt = f"""You are an expert software engineer reviewing a failed test run.
The test output below indicates at least one error, but simple parsing has failed.
Analyze the entire output and identify the specific file(s), line number(s), and root cause(s).

TEST OUTPUT:
---
{state.current_test_results.output}
---

INSTRUCTIONS:
1.  Identify all distinct bugs.
2.  For each bug, provide the file path, the exact line number, and a concise error message.
3.  Return the result as a JSON array of objects in the format: `[{{ "file_name": string, "line_number": int, "error_message": string }}]`.
4.  If you cannot determine the exact file or line, make a best guess.
5.  Return ONLY the JSON array inside a ```json block.

Example:
```json
[
  {{
    "file_name": "src/utils.py",
    "line_number": 42,
    "error_message": "TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'"
  }}
]
```
"""
                ai_output = await call_ai(client, prompt)
                if ai_output:
                    json_str = extract_json(ai_output)
                    if json_str:
                        try:
                            parsed_failures = json.loads(json_str)
                            for failure_data in parsed_failures:
                                failures.append(BugMetadata(
                                    file_name=failure_data.get("file_name", "Unknown"),
                                    line_number=failure_data.get("line_number", 1),
                                    error_message=f"[AI Analysis] {failure_data.get('error_message', 'Unknown error')}",
                                    bug_type="LOGIC"  # Default to LOGIC for AI-found errors
                                ))
                            print(f"INFO: LLM Fallback identified {len(failures)} potential failure(s).")
                        except json.JSONDecodeError:
                            print(f"ERROR: LLM fallback failed to produce valid JSON. Response: {json_str[:200]}")
                    else:
                        print(f"ERROR: Could not extract JSON from LLM fallback response. Response: {ai_output[:200]}")
            except Exception as e:
                print(f"ERROR during LLM fallback analysis: {e}")

    # Final fallback if all else fails
    if not failures and state.current_test_results.total_failures > 0:
        target_file = "main.py"
        if state.repo_path and os.path.exists(state.repo_path):
            py_files = [f for f in os.listdir(state.repo_path) if f.endswith('.py')]
            if py_files:
                target_file = py_files[0]
        failures.append(BugMetadata(
            file_name=target_file,
            line_number=1,
            error_message="Agent detected an unidentifiable issue. A full logic audit may be required.",
            bug_type="LOGIC"
        ))

    state.current_test_results.failures = failures
    print(f"DEBUG: Analyzer identified {len(failures)} failures total")
    return state
