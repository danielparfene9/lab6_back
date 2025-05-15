from pydantic import BaseModel, Field


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

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 60