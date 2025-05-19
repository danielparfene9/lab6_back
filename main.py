from fastapi import FastAPI
from auth.auth_router import router as auth_router
from app.routes import router as user_router
from db.alchemy_settings import init_db

app = FastAPI(title="Lab 7 Backend")

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(auth_router)
app.include_router(user_router)
