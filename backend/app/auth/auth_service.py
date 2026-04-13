from datetime import datetime
from backend.app.db.mongo import get_db
from backend.app.core.security import hash_password, verify_password
from backend.app.auth.jwt_handler import create_access_token

async def signup_user(name: str, email: str, password: str):
    db = get_db()
    existing = await db.users.find_one({"email": email})
    if existing:
        return None, "Email already registered"

    user = {
        "name": name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(user)
    token = create_access_token({"sub": str(result.inserted_id)})
    return token, None

async def login_user(email: str, password: str):
    db = get_db()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        return None, "Invalid credentials"

    token = create_access_token({"sub": str(user["_id"])})
    return token, None
