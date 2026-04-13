from pydantic import BaseModel
from datetime import datetime

class LogEntry(BaseModel):
    job_id: str
    step: str
    message: str
    created_at: datetime = None
