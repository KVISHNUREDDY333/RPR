from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from backend.app.models.user_model import UserCreate, UserLogin, UserOut, UserUpdate
from backend.app.auth.auth_service import signup_user, login_user
from backend.app.auth.dependencies import get_current_user
from backend.app.core.security import hash_password, verify_password
from backend.app.db.mongo import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup")
async def signup(body: UserCreate):
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    token, error = await signup_user(body.name, body.email, body.password)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login")
async def login(body: UserLogin):
    token, error = await login_user(body.email, body.password)
    if error:
        raise HTTPException(status_code=401, detail=error)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return UserOut(id=user["id"], name=user["name"], email=user["email"])


@router.put("/profile")
async def update_profile(body: UserUpdate, user=Depends(get_current_user)):
    db = get_db()
    updates = {}

    if body.name and body.name.strip():
        updates["name"] = body.name.strip()

    if body.new_password:
        if not body.current_password:
            raise HTTPException(status_code=400, detail="Current password required")
        if not verify_password(body.current_password, user["password"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if len(body.new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
        updates["password"] = hash_password(body.new_password)

    if not updates:
        raise HTTPException(status_code=400, detail="No changes provided")

    updates["updated_at"] = datetime.utcnow()
    try:
        from bson import ObjectId
        await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": updates})
    except Exception:
        await db.users.update_one({"_id": user["id"]}, {"$set": updates})

    return {"message": "Profile updated successfully"}


@router.get("/stats")
async def get_stats(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.jobs.find({"user_id": user["id"]})
    total = completed = failed = total_words = 0
    scores = []
    async for job in cursor:
        total += 1
        if job["status"] == "completed":
            completed += 1
            total_words += job.get("word_count") or 0
            if job.get("overall_score") is not None:
                scores.append(job["overall_score"])
        elif job["status"] == "failed":
            failed += 1
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    return {
        "total_jobs": total,
        "completed": completed,
        "failed": failed,
        "total_words_processed": total_words,
        "avg_score": avg_score
    }
