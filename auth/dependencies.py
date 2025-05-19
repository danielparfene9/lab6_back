from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from jose import JWTError
from .auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class TokenPayload(BaseModel):
    id: int
    sub: str
    role: str
    exp: int

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        payload = decode_token(token)
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_role(required_roles: list[str]):
    def role_guard(token: str = Depends(oauth2_scheme)) -> TokenPayload:
        try:
            payload = decode_token(token)
            user = TokenPayload(**payload)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_guard

def require_superuser(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    try:
        payload = decode_token(token)
        user = TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user.role != "SUPERUSER":
        raise HTTPException(status_code=403, detail="Superuser access required")
    return user