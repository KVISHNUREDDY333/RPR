from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import PARAPHRASE_PROMPT

async def paraphrase(text: str) -> str:
    return await call_llm(PARAPHRASE_PROMPT, text)
