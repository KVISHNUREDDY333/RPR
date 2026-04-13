import os
import uuid
from pathlib import Path
from backend.app.core.settings import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}

def save_upload(file_bytes: bytes, filename: str) -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not supported")
    
    job_id = str(uuid.uuid4())
    dest = os.path.join(settings.UPLOAD_DIR, f"{job_id}{ext}")
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(dest, "wb") as f:
        f.write(file_bytes)
    
    return job_id, dest
