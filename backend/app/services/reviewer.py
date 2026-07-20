from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import REVIEW_PROMPT

async def review_section(text: str) -> dict:
    try:
        result = await call_llm(REVIEW_PROMPT, text, is_json=True)
        return {
            "clarity_rating": result.get("clarity_rating", "Medium"),
            "issues": result.get("issues", []),
            "suggestions": result.get("suggestions", [])
        }
    except Exception:
        return {"clarity_rating": "Medium", "issues": [], "suggestions": []}
