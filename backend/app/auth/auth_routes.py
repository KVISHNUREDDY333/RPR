from fastapi import APIRouter, HTTPException
from backend.app.models.user_model import UserCreate, UserLogin, UserOut
from backend.app.auth.auth_service import signup_user, login_user
from backend.app.auth.dependencies import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
async def signup(body: UserCreate):
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
