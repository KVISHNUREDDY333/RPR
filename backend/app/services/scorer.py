from backend.app.llm.llm_service import call_llm

SCORING_PROMPT = """Score the following research paper section from 0 to 10 based on academic quality, rigorous methodology, and theoretical contribution.

Return valid JSON:
{
  "score": number, 
  "reason": "string"
}
"""

async def score_section(content: str) -> dict:
    """Assign an academic score to a section."""
    return await call_llm(SCORING_PROMPT, content, is_json=True)
