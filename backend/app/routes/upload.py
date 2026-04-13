from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from datetime import datetime
from backend.app.auth.dependencies import get_current_user
from backend.app.utils.file_utils import save_upload
from backend.app.services.pipeline import run_pipeline
from backend.app.db.mongo import get_db

router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:  # 20MB limit
        raise HTTPException(status_code=413, detail="File too large (max 20MB)")
    
    try:
        job_id, file_path = save_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db = get_db()
    now = datetime.utcnow()
    await db.jobs.insert_one({
        "job_id": job_id,
        "user_id": user["id"],
        "status": "queued",
        "file_path": file_path,
        "original_filename": file.filename,
        "output_path": None,
        "word_count": None,
        "processing_time": None,
        "similarity_score": None,
        "progress": 0,
        "created_at": now,
        "updated_at": now
    })
    
    background_tasks.add_task(run_pipeline, job_id, file_path, user["id"])
    return {"job_id": job_id, "status": "queued"}
