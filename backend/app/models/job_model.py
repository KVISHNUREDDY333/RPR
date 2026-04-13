from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    user_id: str
    file_path: str
    original_filename: str

class JobOut(BaseModel):
    job_id: str
    user_id: str
    status: str
    original_filename: str
    output_path: Optional[str] = None
    word_count: Optional[int] = None
    processing_time: Optional[float] = None
    similarity_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
