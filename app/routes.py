from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db.alchemy_settings import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/test")
def test_route(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).fetchone()
    if result is None:
        return {"ok": False}
    return {"ok": result[0] == 1}