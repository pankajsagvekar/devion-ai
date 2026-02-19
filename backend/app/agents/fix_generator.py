import os
import google.generativeai as genai
from app.state import AgentState
from app.config import GEMINI_API_KEY

async def fix_generator_agent(state: AgentState) -> AgentState:
    """Generates code patches using Gemini API."""
    print("--- FIX GENERATOR AGENT (AI-POWERED) ---")
    
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY is not set. Skipping AI fix generation.")
        return state

    if not state.current_test_results or not state.current_test_results.failures:
        return state

    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Process the first failure (can be extended to multiple)
    failure = state.current_test_results.failures[0]
    file_path = os.path.join(state.repo_path, failure.file_name)

    if not os.path.exists(file_path):
        print(f"ERROR: File not found at {file_path}")
        return state

    # Read the failing file
    with open(file_path, 'r') as f:
        file_content = f.read()

    # Construct the prompt
    prompt = f"""
You are an expert Python developer specialized in CI/CD healing.
A test has failed in a repository. Your task is to fix the code to make the test pass.

FAILING FILE: {failure.file_name}
LINE NUMBER: {failure.line_number}
ERROR MESSAGE: {failure.error_message}
BUG TYPE: {failure.bug_type}

CURRENT FILE CONTENT:
```python
{file_content}
```

INSTRUCTIONS:
1. Analyze the error and the code.
2. Provide the COMPLETELY FIXED content of the file.
3. Return ONLY the code content, wrapped in triple backticks and 'python' language identifier.
4. Do not include any explanations or other text.
"""

    try:
        response = model.generate_content(prompt)
        ai_output = response.text

        # Extract code block
        import re
        code_match = re.search(r"```python\n(.*?)\n```", ai_output, re.DOTALL)
        if code_match:
            fixed_content = code_match.group(1)
            
            # Write the fix back to the file
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            fix_description = f"AI Fix applied to {failure.file_name} for {failure.bug_type} at line {failure.line_number}"
            state.fixes_applied.append(fix_description)
            print(f"SUCCESS: Applied AI fix to {failure.file_name}")
        else:
            print("ERROR: AI response did not contain a valid code block.")
            print(f"AI Response was: {ai_output}")

    except Exception as e:
        print(f"ERROR during AI fix generation: {e}")

    return state
