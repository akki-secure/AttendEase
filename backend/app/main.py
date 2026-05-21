import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models import attendance, user  # noqa: F401 — ensure models are registered before create_all
from app.routers import admin, attendance as attendance_router, auth

app = FastAPI(title="AttendEase API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(attendance_router.router, prefix="/api/v1/attendance", tags=["attendance"])


@app.on_event("startup")
async def startup() -> None:
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
