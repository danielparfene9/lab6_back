from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from db.models import User, Win
from app.schemas import WinCreate, WinOut, WinUpdate
from .dependencies import require_superuser
from db.alchemy_settings import DBSessionSingleton

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    return DBSessionSingleton.get_session()

@router.get("/users/{user_id}/wins", response_model=List[WinOut])
def get_user_wins(user_id: int, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    return db.query(Win).filter(Win.user_id == user_id).all()

@router.post("/users/{user_id}/wins", response_model=WinOut)
def create_user_win(user_id: int, win: WinCreate, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_win = Win(**win.dict(), user_id=user_id)
    db.add(new_win)
    db.commit()
    db.refresh(new_win)
    return new_win

@router.put("/users/{user_id}/wins/{win_id}", response_model=WinOut)
def edit_user_win(user_id: int, win_id: int, update: WinUpdate, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    win = db.query(Win).filter(Win.id == win_id, Win.user_id == user_id).first()
    if not win:
        raise HTTPException(status_code=404, detail="Win not found")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(win, key, value)
    db.commit()
    db.refresh(win)
    return win

@router.delete("/users/{user_id}/wins")
def delete_user_wins(user_id: int, all: bool = Query(False), win_id: Optional[int] = None, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    query = db.query(Win).filter(Win.user_id == user_id)
    if all:
        count = query.delete()
        db.commit()
        return {"msg": f"Deleted {count} wins for user {user_id}"}
    elif win_id:
        win = query.filter(Win.id == win_id).first()
        if not win:
            raise HTTPException(status_code=404, detail="Win not found")
        db.delete(win)
        db.commit()
        return {"msg": f"Deleted win {win_id} for user {user_id}"}
    else:
        raise HTTPException(status_code=400, detail="Provide either 'all=true' or a 'win_id'")

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"msg": f"User {user_id} deleted"}

@router.patch("/users/{user_id}/restrict")
def restrict_user_login(user_id: int, until: datetime, db: Session = Depends(get_db), _ = Depends(require_superuser)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.login_blocked_until = until
    db.commit()
    return {"msg": f"User {user.username} login restricted until {until}"}
