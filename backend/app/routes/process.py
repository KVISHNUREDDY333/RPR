from fastapi import APIRouter, Depends, HTTPException
from backend.app.auth.dependencies import get_current_user
from backend.app.db.mongo import get_db

router = APIRouter(prefix="/api", tags=["process"])

@router.get("/process/{job_id}/logs")
async def get_logs(job_id: str, user=Depends(get_current_user)):
    db = get_db()
    job = await db.jobs.find_one({"job_id": job_id, "user_id": user["id"]})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    cursor = db.logs.find({"job_id": job_id}).sort("created_at", 1)
    logs = []
    async for log in cursor:
        logs.append({
            "step": log["step"],
            "message": log["message"],
            "created_at": log["created_at"].isoformat()
        })
    return logs
