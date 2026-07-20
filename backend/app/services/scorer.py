from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import SCORE_PROMPT

async def score_section(text: str) -> dict:
    try:
        result = await call_llm(SCORE_PROMPT, text, is_json=True)
        score = float(result.get("score", 5.0))
        score = max(0.0, min(10.0, score))
        return {
            "score": round(score, 1),
            "reason": result.get("reason", "No reason provided")
        }
    except Exception:
        return {"score": 5.0, "reason": "Could not evaluate this section"}
