import asyncio
import json
from google import genai
from google.genai import types
from backend.app.core.settings import settings

def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

async def call_llm(prompt: str, content: str, retries: int = 3, is_json: bool = False) -> any:
    """
    Calls the Google Gen AI SDK.
    Supports structured JSON out as requested for RPR v2.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    client = _get_client()
    model_name = settings.GEMINI_MODEL.strip().replace("models/", "")
    
    # Use JSON mode if requested
    response_mime_type = "application/json" if is_json else "text/plain"
    
    config = types.GenerateContentConfig(
        system_instruction=prompt,
        temperature=0.2 if is_json else 0.7,  # Lower temperature for deterministic JSON
        max_output_tokens=4096,
        response_mime_type=response_mime_type
    )

    for attempt in range(retries):
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=content,
                config=config
            )
            
            if not response or not response.text:
                raise RuntimeError("Empty response from LLM")
            
            if is_json:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    # Retry if JSON is malformed
                    if attempt < retries - 1:
                        continue
                    raise RuntimeError("Failed to parse JSON from LLM response")
            
            return response.text
            
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Gemini API failure: {str(e)}")
            await asyncio.sleep(2 ** attempt)
