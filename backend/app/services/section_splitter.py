import re
from typing import List

SECTION_HEADERS = re.compile(
    r"^(abstract|introduction|background|literature review|methodology|"
    r"methods|results|discussion|conclusion|references|acknowledgements?)\s*$",
    re.IGNORECASE | re.MULTILINE
)

def split_sections(text: str) -> List[dict]:
    """Split text into sections. Falls back to paragraph chunks if no headers found."""
    matches = list(SECTION_HEADERS.finditer(text))
    
    if len(matches) >= 2:
        sections = []
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            if content:
                sections.append({"title": match.group().strip(), "content": content})
        return sections
    
    # Fallback: chunk by paragraphs (~500 words each)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks, current, count = [], [], 0
    for para in paragraphs:
        words = len(para.split())
        if count + words > 500 and current:
            chunks.append({"title": f"Section {len(chunks)+1}", "content": "\n\n".join(current)})
            current, count = [], 0
        current.append(para)
        count += words
    if current:
        chunks.append({"title": f"Section {len(chunks)+1}", "content": "\n\n".join(current)})
    return chunks
