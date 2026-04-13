import asyncio
import google.generativeai as genai
from backend.app.core.settings import settings

def _get_model():
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel(settings.GEMINI_MODEL)

async def call_llm(prompt: str, content: str, retries: int = 3) -> str:
    """Calls Google Gemini API with system prompt and user content."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set in .env")

    model = _get_model()
    
    for attempt in range(retries):
        try:
            # Combining system prompt and user content for Gemini
            # (Gemini 1.5 supports system_instruction, but for simplicity/compatibility 
            # we can also just prepend it)
            response = await model.generate_content_async(
                f"{prompt}\n\nContent to process:\n{content}"
            )
            
            if not response.text:
                raise RuntimeError("Empty response from Gemini")
                
            return response.text
            
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Gemini API failed after {retries} attempts: {str(e)}")
            await asyncio.sleep(2 ** attempt)
