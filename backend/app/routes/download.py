from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from backend.app.auth.jwt_handler import decode_token
from backend.app.db.mongo import get_db
import os

router = APIRouter(prefix="/api", tags=["download"])

async def _get_user(token: str):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    db = get_db()
    uid = payload["sub"]
    try:
        from bson import ObjectId
        user = await db.users.find_one({"_id": ObjectId(uid)})
    except Exception:
        user = await db.users.find_one({"_id": uid})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    user["id"] = str(user["_id"])
    return user

@router.get("/download/{job_id}")
async def download_result(job_id: str, token: str = Query(...)):
    user = await _get_user(token)
    db = get_db()
    job = await db.jobs.find_one({"job_id": job_id, "user_id": user["id"]})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job status: {job['status']}")

    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    name_no_ext = os.path.splitext(job.get("original_filename", job_id))[0]
    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"refined_{name_no_ext}.docx"
    )
