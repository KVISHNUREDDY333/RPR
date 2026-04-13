import asyncio
from google import genai
from google.genai import types
from backend.app.core.settings import settings

def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

async def call_llm(prompt: str, content: str, retries: int = 3) -> str:
    """Calls the official Google Gen AI SDK."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    client = _get_client()
    
    # Cleaning the model name just in case
    model_name = settings.GEMINI_MODEL.strip().replace("models/", "")
    
    config = types.GenerateContentConfig(
        system_instruction=prompt,
        temperature=0.7,
        max_output_tokens=2048,
    )

    for attempt in range(retries):
        try:
            # Using the modern asynchronous interface
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=content,
                config=config
            )
            
            if not response or not response.text:
                raise RuntimeError("Empty response from Gemini")
                
            return response.text
            
        except Exception as e:
            # Check for common errors
            err_str = str(e)
            if "404" in err_str:
                raise RuntimeError(f"Model '{model_name}' not found. Please check your GEMINI_MODEL in .env. Error: {err_str}")
            
            if attempt == retries - 1:
                raise RuntimeError(f"Gemini API failure: {err_str}")
            
            await asyncio.sleep(2 ** attempt)
