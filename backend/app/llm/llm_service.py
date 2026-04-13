import httpx
import asyncio
from backend.app.core.settings import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def call_groq(prompt: str, content: str, retries: int = 3) -> str:
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }
    
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(GROQ_URL, json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Groq API failed after {retries} attempts: {e}")
            await asyncio.sleep(2 ** attempt)
