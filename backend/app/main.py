import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.session import SessionLocal, Base, engine
from app.database.init_db import init_and_seed_db
from app.ai.generator import is_ai_configured

# Import API Routers
from app.api.auth import router as auth_router
from app.api.courses import router as courses_router
from app.api.sections import router as sections_router
from app.api.quizzes import router as quizzes_router
from app.api.student import router as student_router
from app.api.admin import router as admin_router
from app.api.analytics import router as analytics_router
from app.api.notifications import router as notifications_router
from app.api.certificates import router as certificates_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up... Initializing database & seed verification.")
    db = SessionLocal()
    try:
        init_and_seed_db(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Intelligent AI-Powered University Learning Management System",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local storage for static assets & documents
app.mount("/storage", StaticFiles(directory=settings.BASE_STORAGE_DIR), name="storage")

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(courses_router, prefix=settings.API_V1_STR)
app.include_router(sections_router, prefix=settings.API_V1_STR)
app.include_router(quizzes_router, prefix=settings.API_V1_STR)
app.include_router(student_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(notifications_router, prefix=settings.API_V1_STR)
app.include_router(certificates_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs",
        "ai_mode": "Groq AI Cloud" if is_ai_configured() else "Local Deterministic Demo Engine"
    }

@app.get("/api/info")
def platform_info():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "ai_active": is_ai_configured(),
        "ai_provider": "Groq API (Llama 3.3 70B)" if is_ai_configured() else "Local Deterministic University Demo Engine",
        "demo_accounts": [
            {"role": "Teacher", "email": "teacher@eduai.demo", "password": "password123"},
            {"role": "Student", "email": "student@eduai.demo", "password": "password123"},
            {"role": "Administrator", "email": "admin@eduai.demo", "password": "password123"}
        ]
    }
