from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ==== User Schemas ====

class UserBase(BaseModel):
    username: str = Field(...)

class UserCreate(UserBase):
    password: str = Field(...)
    role: str = Field(...)

class UserOut(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True

# ==== Token Schemas ====

class TokenRequest(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==== Win Schemas ====

class WinBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = Field(default_factory=datetime.utcnow)

class WinCreate(WinBase):
    pass

class WinUpdate(WinBase):
    pass

class WinOut(WinBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True