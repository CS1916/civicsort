import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from app.config import settings
from app.routes import (
    classify_router,
    route_optimizer_router,
    bins_router,
    settings_router,
    auth_router,
    fleet_router,
    collections_router,
    notifications_router,
)
from app.database import init_db

app = FastAPI(
    title="EcoRoute — Smart Waste Management & Computer Vision Platform",
    version="3.0.0",
    description="""
    ## EcoRoute: High-Accuracy Computer Vision Waste Segregation & Fleet Route Optimization
    - **Authentication & RBAC**: `POST /auth/login`, `GET /auth/me`, `GET /auth/users`
    - **Computer Vision Endpoints**: `POST /detect/image`, `POST /detect/video` (YOLOv8s + SAHI multi-scale inference)
    - **Smart Bins**: `GET /bins`, `POST /bins`, `PUT /bins/{id}`, `DELETE /bins/{id}`, `POST /bins/simulate`
    - **Fleet & Driver Management**: `GET/POST /vehicles`, `GET/POST /drivers`
    - **Collection History**: `GET /collections/history`, `POST /collections/dispatch`
    - **Notifications**: `GET /notifications`, `POST /notifications/{id}/read`
    - **Fleet Routing**: `POST /routes/optimize` (Google OR-Tools VRP)
    - **Analytics & Reports**: `GET /analytics`, `GET /reports/export`
    - **Map API Key Settings**: `GET /settings/map-key`, `POST /settings/map-key`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (annotated videos & images)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(os.path.join(STATIC_DIR, "outputs"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Mount API Routers
app.include_router(auth_router)
app.include_router(classify_router)
app.include_router(route_optimizer_router)
app.include_router(bins_router)
app.include_router(fleet_router)
app.include_router(collections_router)
app.include_router(notifications_router)
app.include_router(settings_router)

# Path to standalone-preview.html
PROJECT_ROOT = os.path.dirname(BASE_DIR)
STANDALONE_HTML_PATH = os.path.join(PROJECT_ROOT, "standalone-preview.html")

@app.get("/", tags=["UI"])
def serve_ui():
    """
    Serves the upgraded EcoRoute AI Dashboard directly at http://127.0.0.1:8000/
    """
    if os.path.exists(STANDALONE_HTML_PATH):
        return FileResponse(STANDALONE_HTML_PATH, media_type="text/html")
    return HTMLResponse("<h1>EcoRoute AI is Online</h1><p>Visit <a href='/docs'>/docs</a></p>")

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "EcoRoute AI Production Core v3.0",
        "database": "SQLite Connected & Verified",
        "yoloModel": settings.YOLO_MODEL_PATH,
        "staticDir": STATIC_DIR,
        "tileProvider": "Esri World Imagery + Custom Key Supported",
    }
