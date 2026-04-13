from backend.app.llm.llm_service import call_groq
from backend.app.llm.prompts import GRAMMAR_PROMPT

async def improve_grammar(text: str) -> str:
    return await call_groq(GRAMMAR_PROMPT, text)
