from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, admissions, auth, chat, innovation, systems, website
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admissions.router, prefix="/api")
app.include_router(website.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(systems.router, prefix="/api")
app.include_router(innovation.router, prefix="/api")
Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root() -> dict:
    return {"name": settings.app_name, "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@app.get("/debug/counts")
def debug_counts() -> dict:
    from app.core.database import SessionLocal
    from app.models.models import GradeRecord, Major, Score, SiteArticle, StudentRecord, User

    with SessionLocal() as db:
        return {
            "database": "sqlite" if settings.use_sqlite else "mysql",
            "users": db.query(User).count(),
            "majors": db.query(Major).count(),
            "scores": db.query(Score).count(),
            "articles": db.query(SiteArticle).count(),
            "students": db.query(StudentRecord).count(),
            "grades": db.query(GradeRecord).count(),
        }
