from backend.app.llm.llm_service import call_llm

REVIEW_PROMPT = """Analyze the following research paper section for academic excellence.
Focus on clarity, research depth, and writing quality.

Return valid JSON:
{
  "clarity_rating": "string (clear/moderate/needs-work)",
  "depth_analysis": "string",
  "issues": ["string"],
  "improvement_suggestions": "string"
}
"""

async def review_section(content: str) -> dict:
    """Analyze a single section and return structured review data."""
    return await call_llm(REVIEW_PROMPT, content, is_json=True)
