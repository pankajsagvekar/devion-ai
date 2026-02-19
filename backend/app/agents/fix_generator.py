import os
import re
import time
import asyncio
from google import genai
from app.state import AgentState
from app.config import GEMINI_API_KEY

async def fix_generator_agent(state: AgentState) -> AgentState:
    """Generates code patches using Gemini API with fallback strategy."""
    print("--- FIX GENERATOR AGENT (AI-POWERED) ---")
    
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is not set. Skipping AI fix generation.")
        return state

    if not state.current_test_results or not state.current_test_results.failures:
        return state

    # Initialize GenAI Client
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"ERROR initializing GenAI client: {e}")
        state.final_status = "AI_CONFIG_ERROR"
        return state

    # Process the first failure
    failure = state.current_test_results.failures[0]
    file_path = os.path.join(state.repo_path, failure.file_name)

    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        return state

    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
    except Exception as e:
        print(f"ERROR reading file {file_path}: {e}")
        return state

    prompt = f"""
You are an expert Python developer. Fix this code to make the test pass.
ERROR: {failure.error_message} at line {failure.line_number}
FILE: {failure.file_name}

CONTENT:
```python
{file_content}
```

Return ONLY the completely fixed code in a single python block.
"""

    # Multi-model fallback strategy
    models_to_try = [
        "gemini-2.0-flash-lite", 
        "gemini-flash-latest",
        "gemini-exp-1206"
    ]
    
    ai_output = None
    last_error = ""

    for model_name in models_to_try:
        try:
            print(f"DEBUG: [Agent Check] Requesting AI fix from {model_name}...")
            # Use synchronous call but wrap in current state
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            ai_output = response.text
            print(f"DEBUG: [Agent Check] Received response from {model_name}")
            break # Success!
        except Exception as e:
            last_error = str(e)
            if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                print(f"WARNING: Quota hit for {model_name}. Retrying with next model...")
                await asyncio.sleep(1) # Async pause
                continue
            else:
                print(f"ERROR with {model_name}: {last_error}")
                break # Non-quota error, don't fallback

    if not ai_output:
        if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
             print("CRITICAL: All models reached quota limits (429). Please wait a few minutes or check https://aistudio.google.com/app/plan")
        else:
             print(f"CRITICAL: AI Generation failed: {last_error}")
        state.final_status = "FAILED"
        return state

    # Extract and apply fix
    code_match = re.search(r"```python\n(.*?)\n```", ai_output, re.DOTALL)
    if not code_match:
        # Try fallback matching without 'python' label
        code_match = re.search(r"```\n(.*?)\n```", ai_output, re.DOTALL)

    if code_match:
        fixed_content = code_match.group(1)
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        fix_description = f"AI Fix applied to {failure.file_name} for {failure.bug_type} at line {failure.line_number}"
        state.fixes_applied.append(fix_description)
        print(f"SUCCESS: Applied AI fix to {failure.file_name}")
    else:
        print("ERROR: AI response did not contain a valid code block.")
        print(f"AI Response was: {ai_output}")
        state.final_status = "FAILED"

    return state
