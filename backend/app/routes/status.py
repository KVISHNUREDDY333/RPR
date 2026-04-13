from fastapi import APIRouter, Depends, HTTPException
from backend.app.auth.dependencies import get_current_user
from backend.app.db.mongo import get_db

router = APIRouter(prefix="/api", tags=["status"])

@router.get("/status/{job_id}")
async def get_status(job_id: str, user=Depends(get_current_user)):
    db = get_db()
    job = await db.jobs.find_one({"job_id": job_id, "user_id": user["id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "original_filename": job.get("original_filename"),
        "overall_score": job.get("overall_score"),
        "analysis": job.get("analysis", []),
        "feedback": job.get("feedback", {}),
        "processing_time": job.get("processing_time"),
        "error": job.get("error"),
        "created_at": job["created_at"].isoformat(),
        "updated_at": job["updated_at"].isoformat()
    }

@router.get("/jobs")
async def list_jobs(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.jobs.find({"user_id": user["id"]}).sort("created_at", -1).limit(20)
    jobs = []
    async for job in cursor:
        jobs.append({
            "job_id": job["job_id"],
            "status": job["status"],
            "original_filename": job.get("original_filename"),
            "overall_score": job.get("overall_score"),
            "created_at": job["created_at"].isoformat()
        })
    return jobs
