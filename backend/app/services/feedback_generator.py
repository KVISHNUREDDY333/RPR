from backend.app.llm.llm_service import call_llm

FEEDBACK_PROMPT = """Provide a high-level aggregate feedback for the overall research paper based on the summarized findings.

Return valid JSON:
{
  "strengths": ["string"],
  "weaknesses": ["string"],
  "suggestions": ["string"],
  "final_verdict": "string"
}
"""

async def generate_overall_feedback(summarized_analysis: str) -> dict:
    """Generate global strengths, weaknesses, and suggestions based on aggregated section reviews."""
    return await call_llm(FEEDBACK_PROMPT, summarized_analysis, is_json=True)
