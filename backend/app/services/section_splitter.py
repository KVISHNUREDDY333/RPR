import re
from typing import List

SECTION_HEADERS = re.compile(
    r"^(abstract|introduction|background|literature review|methodology|"
    r"methods|results|discussion|conclusion|references|acknowledgements?)\s*$",
    re.IGNORECASE | re.MULTILINE
)

def split_sections(text: str) -> List[dict]:
    """Split text into sections. Ensures no section is too large for LLM processing."""
    matches = list(SECTION_HEADERS.finditer(text))
    
    # 1. First pass: Identify sections based on headers
    raw_sections = []
    if len(matches) >= 2:
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            if content:
                raw_sections.append({"title": match.group().strip(), "content": content})
    else:
        # Fallback if no headers found
        raw_sections = [{"title": "Paper Content", "content": text}]

    # 2. Second pass: Split sections that are too long (>1000 words)
    final_sections = []
    for section in raw_sections:
        words = section["content"].split()
        if len(words) > 1000:
            # Chunk this large section into ~800 word pieces
            current_chunk = []
            word_count = 0
            chunk_index = 1
            
            # Split by paragraphs to preserve meaning
            paragraphs = section["content"].split("\n\n")
            for p in paragraphs:
                p_words = len(p.split())
                if word_count + p_words > 800 and current_chunk:
                    final_sections.append({
                        "title": f"{section['title']} (Part {chunk_index})",
                        "content": "\n\n".join(current_chunk).strip()
                    })
                    current_chunk = [p]
                    word_count = p_words
                    chunk_index += 1
                else:
                    current_chunk.append(p)
                    word_count += p_words
            
            if current_chunk:
                final_sections.append({
                    "title": f"{section['title']} (Part {chunk_index})",
                    "content": "\n\n".join(current_chunk).strip()
                })
        else:
            final_sections.append(section)

    return [s for s in final_sections if s["content"]]
