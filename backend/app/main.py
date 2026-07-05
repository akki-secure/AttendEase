import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, attendance as attendance_router, auth, leaves, notifications as notifications_router, overtime as overtime_router, profile as profile_router, reports as reports_router

app = FastAPI(title="AttendEase API", version="1.0.0")

_default_origins = "http://localhost:3000"
allow_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOW_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(attendance_router.router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(leaves.router)
app.include_router(overtime_router.router)
app.include_router(reports_router.router)
app.include_router(notifications_router.router)
app.include_router(profile_router.router)


@app.on_event("startup")
async def startup() -> None:
    os.makedirs("data", exist_ok=True)
