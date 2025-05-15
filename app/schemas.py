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