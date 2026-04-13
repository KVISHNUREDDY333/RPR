from fastapi import APIRouter
from backend.app.db.mongo import get_db

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health():
    try:
        db = get_db()
        await db.command("ping")
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}
