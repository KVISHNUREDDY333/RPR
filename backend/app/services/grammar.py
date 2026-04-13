from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import GRAMMAR_PROMPT

async def improve_grammar(text: str) -> str:
    return await call_llm(GRAMMAR_PROMPT, text)
