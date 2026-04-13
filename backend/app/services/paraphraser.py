from backend.app.llm.llm_service import call_groq
from backend.app.llm.prompts import PARAPHRASE_PROMPT

async def paraphrase(text: str) -> str:
    return await call_groq(PARAPHRASE_PROMPT, text)
