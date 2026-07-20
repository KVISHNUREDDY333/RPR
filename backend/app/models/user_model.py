from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
