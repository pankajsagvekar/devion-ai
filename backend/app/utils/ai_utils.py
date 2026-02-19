import re
import asyncio
from typing import Optional
from google import genai

MODELS_TO_TRY = [
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-exp-1206"
]

async def call_ai(client, prompt: str) -> Optional[str]:
    """Try each model in order, return the first successful response text."""
    last_error = ""
    for model_name in MODELS_TO_TRY:
        print(f"DEBUG: [AI] Requesting from {model_name}...")
        retry_attempts = 0
        while retry_attempts < 2:
            try:
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model_name,
                    contents=prompt
                )
                print(f"DEBUG: [AI] Received response from {model_name}")
                return response.text
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                    import re as _re
                    delay_match = _re.search(r"retryDelay.*?(\d+)s", last_error)
                    retry_after = int(delay_match.group(1)) + 2 if delay_match else 15
                    # Target wait time under 20 seconds
                    retry_after = min(retry_after, 19)
                    print(f"WARNING: Quota hit for {model_name}. Waiting {retry_after}s... (Attempt {retry_attempts+1}/2)")
                    await asyncio.sleep(retry_after)
                    retry_attempts += 1
                    continue
                print(f"ERROR with {model_name}: {last_error}")
                break
        
        # If we exhausted retry attempts for this model, we move to the next model in the outer loop
        continue
    
    print(f"CRITICAL: All AI models failed. Last error: {last_error[:200]}")
    return None


def extract_code(ai_output: str) -> Optional[str]:
    """Extract python code block from AI response."""
    match = re.search(r"```python\n(.*?)\n```", ai_output, re.DOTALL)
    if not match:
        # Fallback for responses that might just use ```
        match = re.search(r"```\n(.*?)\n```", ai_output, re.DOTALL)
    return match.group(1).strip() if match else None

def extract_json(ai_output: str) -> Optional[str]:
    """Extract JSON block from AI response."""
    match = re.search(r"```json\n(.*?)\n```", ai_output, re.DOTALL)
    return match.group(1).strip() if match else None
