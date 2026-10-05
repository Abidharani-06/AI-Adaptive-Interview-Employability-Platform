import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add backend directory and project root to sys.path
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database import engine, Base, init_db
import models
from routers import (
    auth_router,
    profile_router,
    resume_router,
    job_router,
    interview_router,
    assessment_router,
    aptitude_router
)

# Initialize database schema tables and safe SQLite migrations
init_db()

app = FastAPI(
    title="AI Interview & Multimodal Employability Platform API",
    description="Real-world multi-user AI interview platform integrating Phases 1-8 AI/ML pipelines with Round 1 Aptitude & Round 2 HR interview.",
    version="2.1.0"
)

# Robust CORS configuration for 5173, 5174, 5175, 3000, and dynamic origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
if allowed_origins_env:
    for o in allowed_origins_env.split(","):
        if o.strip() and o.strip() not in origins:
            origins.append(o.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router.router)
app.include_router(aptitude_router.router)
app.include_router(profile_router.router)
app.include_router(resume_router.router)
app.include_router(job_router.router)
app.include_router(interview_router.router)
app.include_router(assessment_router.router)


@app.get("/api/health")
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Interview & Employability Platform Backend",
        "version": "2.1.0",
        "rounds": {
            "round_1": "Adaptive Aptitude (Quantitative, Logical, Verbal)",
            "round_2": "AI HR & Behavioral Interview with Speech-to-Text",
            "round_3": "Technical Core Interview",
            "round_4": "Multimodal Assessment (Speech, CV, NLP Fusion)"
        },
        "database": "connected"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Graceful global exception handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting AI Interview Backend on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=True)

