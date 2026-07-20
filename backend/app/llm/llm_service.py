import asyncio
import json
import httpx
from backend.app.core.settings import settings

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def call_llm(prompt: str, content: str, retries: int = 3, is_json: bool = False) -> any:
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your-groq-api-key-here":
        raise RuntimeError("GROQ_API_KEY is not configured in .env")

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    system_msg = prompt
    if is_json:
        system_msg += "\n\nRespond ONLY with valid JSON. No markdown, no explanation."

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": content}
        ],
        "temperature": 0.2 if is_json else 0.7,
        "max_tokens": 4096
    }

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                resp = await client.post(GROQ_URL, json=payload, headers=headers)
                resp.raise_for_status()
                text = resp.json()["choices"][0]["message"]["content"].strip()

            if is_json:
                # Strip markdown code fences if present
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text)

            return text

        except json.JSONDecodeError:
            if attempt == retries - 1:
                raise RuntimeError("LLM returned invalid JSON")
            await asyncio.sleep(1)
        except Exception as e:
            if attempt == retries - 1:
                raise RuntimeError(f"Groq API failed: {str(e)}")
            await asyncio.sleep(2 ** attempt)
