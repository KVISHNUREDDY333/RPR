from backend.app.llm.llm_service import call_llm
from backend.app.llm.prompts import FEEDBACK_PROMPT

async def generate_overall_feedback(analysis_summary: str) -> dict:
    try:
        result = await call_llm(FEEDBACK_PROMPT, analysis_summary, is_json=True)
        return {
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "suggestions": result.get("suggestions", []),
            "summary": result.get("summary", "")
        }
    except Exception:
        return {
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["Please review the document manually."],
            "summary": "Automated feedback could not be generated."
        }
