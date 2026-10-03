"""RecoverMate API — Demo Arena / Night Game pilot."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import ensure_schema
from .routes import admin, auth, found_items, health, lost_reports, matches, venues
from .seed import seed

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_schema()
    seed()
    yield


app = FastAPI(
    title="RecoverMate API",
    description="B2B lost-and-found for stadiums & arenas — Demo Arena pilot",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api")
app.include_router(venues.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(lost_reports.router, prefix="/api")
app.include_router(found_items.router, prefix="/api")
app.include_router(matches.router, prefix="/api")

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def root():
    return {
        "service": "RecoverMate",
        "pilot": "Demo Arena — Night Game",
        "docs": "/docs",
        "health": "/health",
    }
