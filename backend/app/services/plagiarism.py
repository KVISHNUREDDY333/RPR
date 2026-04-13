from sentence_transformers import SentenceTransformer, util
import numpy as np

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def estimate_similarity(original: str, refined: str) -> float:
    """Returns cosine similarity score between 0 and 1."""
    model = _get_model()
    emb1 = model.encode(original[:2000], convert_to_tensor=True)
    emb2 = model.encode(refined[:2000], convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(score, 4)
