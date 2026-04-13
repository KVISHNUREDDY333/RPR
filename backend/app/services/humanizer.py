from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import HUMANIZER_PROMPT

async def humanize(text: str) -> str:
    return await call_llm(HUMANIZER_PROMPT, text)
