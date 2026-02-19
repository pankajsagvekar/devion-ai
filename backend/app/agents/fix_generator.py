import os
import re
import asyncio
from collections import defaultdict
from google import genai
from app.state import AgentState, CommitEntry
from app.config import GEMINI_API_KEY
from app.utils.ai_utils import call_ai, extract_code


async def fix_generator_agent(state: AgentState) -> AgentState:
    """Generates code patches for ALL detected failures concurrently."""
    print("--- FIX GENERATOR AGENT (MULTI-FILE MODE) ---")

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is not set.")
        return state

    if not state.current_test_results or not state.current_test_results.failures:
        return state

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"ERROR initializing GenAI client: {e}")
        state.final_status = "AI_CONFIG_ERROR"
        return state

    failures = state.current_test_results.failures
    print(f"DEBUG: Processing {len(failures)} failure(s) across potentially multiple files.")

    failures_by_file: dict = defaultdict(list)
    for failure in failures:
        failures_by_file[failure.file_name].append(failure)

    any_fix_applied = False

    async def process_file(file_name, file_failures):
        file_path = os.path.join(state.repo_path, file_name)

        if all(f.action == "DELETE" for f in file_failures):
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    return {
                        "type": "delete",
                        "file_name": file_name,
                        "desc": f"LOGIC error in {file_name} line 1 → Fix: remove the redundant or harmful file",
                        "failures": file_failures,
                        "action_desc": "remove the redundant or harmful file"
                    }
                except Exception as e:
                    print(f"ERROR deleting {file_path}: {e}")
            return None

        if not os.path.exists(file_path):
            print(f"ERROR: File not found at {file_path} — skipping.")
            return None

        try:
            with open(file_path, 'r') as f:
                file_content = f.read()
        except Exception as e:
            print(f"ERROR reading {file_path}: {e}")
            return None

        bug_summary = "\n".join(
            f"  - Line {fb.line_number}: [{fb.bug_type}] {fb.error_message}"
            for fb in file_failures
        )

        prompt = f"""You are an expert Python developer. Fix ALL the bugs listed below in this file.

FILE: {file_name}

BUGS TO FIX:
{bug_summary}

CURRENT CODE:
```python
{file_content}
```

INSTRUCTIONS:
1. Fix every reported bug listed above.
2. REMOVE any redundant, dead, or harmful code causing instability.
3. Keep the logic clean and professional.
4. IMPORTANT: You must return the completely fixed code in a single python block.
5. AFTER the python block, you MUST provide a single short sentence describing exactly what you did for the main fix, starting with 'ACTION: '.
   Example: ACTION: remove the unused import statement
"""
        ai_output = await call_ai(client, prompt)
        if not ai_output:
            print(f"CRITICAL: AI fix generation failed for {file_name}.")
            return {"type": "fail", "file_name": file_name}

        fixed_code = extract_code(ai_output)
        
        # Extract action description
        action_desc = "apply necessary code changes"
        for line in ai_output.split('\n'):
            if line.startswith("ACTION: "):
                action_desc = line.replace("ACTION: ", "").strip()
                break

        if fixed_code:
            # We must use exactly one primary failure for the string match, or generate multiple log entries.
            # We will generate the desc based on the first failure to match the strict format perfectly. 
            primary_bug = file_failures[0]
            strict_desc = f"{primary_bug.bug_type} error in {file_name} line {primary_bug.line_number} → Fix: {action_desc}"

            return {
                "type": "fix",
                "file_name": file_name,
                "file_path": file_path,
                "fixed_code": fixed_code,
                "desc": strict_desc,
                "failures": file_failures,
                "action_desc": action_desc
            }
        else:
            print(f"ERROR: AI response for {file_name} had no valid code block. Response: {ai_output[:300]}")
            return None

    # Run AI analysis for multiple files concurrently
    tasks = [process_file(f_name, f_fails) for f_name, f_fails in failures_by_file.items()]
    results = await asyncio.gather(*tasks)

    # Apply results
    for result in results:
        if not result:
            continue
            
        if result["type"] == "fail":
            state.final_status = "FAILED"
            continue
            
        if result["type"] in ["delete", "fix"]:
            if result["type"] == "fix":
                with open(result["file_path"], 'w') as f:
                    f.write(result["fixed_code"])
                    
            state.fixes_applied.append(result["desc"])
            print(f"SUCCESS: {result['desc']}")
            any_fix_applied = True
            
            status_text = "FAILED" if result["type"] == "fail" else "FIXED"
            # We append the exact string match format to fixes_applied directly
            state.fixes_applied.append(result["desc"])
            
            for fb in result["failures"]:
                strict_commit_msg = f"{fb.bug_type} error in {result['file_name']} line {fb.line_number} → Fix: {result.get('action_desc', 'apply code changes')}"
                state.commit_log.append(CommitEntry(
                    file=result["file_name"],
                    bug_type=fb.bug_type,
                    line=fb.line_number,
                    commit_message=strict_commit_msg,
                    status=status_text
                ))

    if not any_fix_applied and state.final_status != "PASSED":
        print("WARNING: No fixes were applied this iteration. Marking as FAILED.")
        state.final_status = "FAILED"

    return state

