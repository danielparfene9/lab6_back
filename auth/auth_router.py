from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from db.alchemy_settings import get_db
from db.models import User
from app.schemas import TokenData, TokenRequest
from auth.auth import create_access_token
from utils.security import verify_password
from datetime import timedelta

router = APIRouter(prefix="/token", tags=["Auth"])

@router.post("", response_model=TokenData)
def login(data: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=1)
    )

    return TokenData(access_token=token, expires_in=60)