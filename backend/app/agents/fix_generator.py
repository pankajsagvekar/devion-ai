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
                        "desc": f"AI Action: DELETED redundant/harmful file {file_name}",
                        "failures": file_failures
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
4. Return ONLY the completely fixed code in a single python block.
"""
        ai_output = await call_ai(client, prompt)
        if not ai_output:
            print(f"CRITICAL: AI fix generation failed for {file_name}.")
            return {"type": "fail", "file_name": file_name}

        fixed_code = extract_code(ai_output)
        if fixed_code:
            return {
                "type": "fix",
                "file_name": file_name,
                "file_path": file_path,
                "fixed_code": fixed_code,
                "desc": f"AI Fix applied to {file_name} for {', '.join(set(fb.bug_type for fb in file_failures))} ({len(file_failures)} issue(s))",
                "failures": file_failures
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
            
            status_text = "DELETED" if result["type"] == "delete" else "FIXED"
            for fb in result["failures"]:
                state.commit_log.append(CommitEntry(
                    file=result["file_name"],
                    bug_type=fb.bug_type,
                    line=fb.line_number,
                    commit_message=f"[AI-AGENT] {status_text} {result['file_name']}",
                    status=status_text
                ))

    if not any_fix_applied and state.final_status != "PASSED":
        print("WARNING: No fixes were applied this iteration. Marking as FAILED.")
        state.final_status = "FAILED"

    return state

