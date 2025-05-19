from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from db.models import User
from db.alchemy_settings import DBSessionSingleton, init_db
from .auth import create_access_token
from app.schemas import UserCreate, TokenRequest, TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === HELPERS ===

def get_db():
    return DBSessionSingleton.get_session()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# === ROUTES ===

@router.post("/register", status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": f"User '{user.username}' registered successfully."}

@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    elif user.login_blocked_until and user.login_blocked_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Login temporarily restricted")

    token = create_access_token({"sub": user.username, "id": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
