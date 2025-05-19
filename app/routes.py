from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import Win, User
from .schemas import WinCreate, WinOut, WinUpdate
from auth.dependencies import get_current_user
from db.alchemy_settings import DBSessionSingleton
from typing import List

router = APIRouter(prefix="/wins", tags=["Wins"])

def get_db():
    return DBSessionSingleton.get_session()

@router.get("/me", response_model=List[WinOut])
def get_my_wins(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Win).filter(Win.user_id == current_user.id).all()

@router.post("/me", response_model=WinOut)
def add_win(win: WinCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_win = Win(**win.dict(), user_id=current_user.id)
    db.add(new_win)
    db.commit()
    db.refresh(new_win)
    return new_win

@router.put("/me/{win_id}", response_model=WinOut)
def edit_win(win_id: int, update: WinUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    win = db.query(Win).filter(Win.id == win_id, Win.user_id == current_user.id).first()
    if not win:
        raise HTTPException(status_code=404, detail="Win not found")

    for key, value in update.dict(exclude_unset=True).items():
        setattr(win, key, value)

    db.commit()
    db.refresh(win)
    return win

@router.delete("/me/{win_id}")
def remove_win(win_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    win = db.query(Win).filter(Win.id == win_id, Win.user_id == current_user.id).first()
    if not win:
        raise HTTPException(status_code=404, detail="Win not found")

    db.delete(win)
    db.commit()
    return {"msg": f"Win {win_id} deleted"}
