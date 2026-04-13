import asyncio
from google import genai
from google.genai import types
from backend.app.core.settings import settings

def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

async def call_llm(prompt: str, content: str, retries: int = 3) -> str:
    """Calls the new, unified Google Gen AI SDK (google-genai)."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    client = _get_client()
    
    # Use proper GenerateContentConfig for system instructions and parameters
    config = types.GenerateContentConfig(
        system_instruction=prompt,
        temperature=0.7,
        max_output_tokens=2048,
    )

    for attempt in range(retries):
        try:
            # Utilizing the modern async 'aio' interface of the google-genai SDK
            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=content,
                config=config
            )
            
            if not response.text:
                raise RuntimeError("Empty response from Gemini")
                
            return response.text
            
        except Exception as e:
            if attempt == retries - 1:
                # Provide a clean error message for the dashboard
                raise RuntimeError(f"Gemini API failure: {str(e)}")
            await asyncio.sleep(2 ** attempt)
