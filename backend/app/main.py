from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import os

from backend.app.db.mongo import connect_db, close_db
from backend.app.auth.auth_routes import router as auth_router
from backend.app.routes.upload import router as upload_router
from backend.app.routes.status import router as status_router
from backend.app.routes.process import router as process_router
from backend.app.routes.download import router as download_router
from backend.app.routes.health import router as health_router
from backend.app.core.settings import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    yield
    await close_db()

app = FastAPI(
    title="RPR - AI Research Paper Refinement",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(status_router)
app.include_router(process_router)
app.include_router(download_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return RedirectResponse(url="/pages/index.html")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    print("[RPR] Frontend served from: " + FRONTEND_DIR)
else:
    print("[RPR] WARNING: Frontend directory not found: " + FRONTEND_DIR)
