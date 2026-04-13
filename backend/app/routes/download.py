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
async def download_result(job_id: str, type: str = "refined", token: str = Query(...)):
    user = await _get_user(token)
    db = get_db()
    job = await db.jobs.find_one({"job_id": job_id, "user_id": user["id"]})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if type == "report":
        path = job.get("report_path")
        filename = f"Review_Report_{job_id}.docx"
    else:
        path = job.get("output_path")
        filename = f"Refined_{job.get('original_filename', job_id)}.docx"

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )
