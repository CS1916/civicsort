from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import classify_router, route_optimizer_router, bins_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## Computer Vision Based Waste Segregation and Intelligent Collection Route Optimization for Sustainable Urban Waste Management

    ### Capabilities:
    1. **Computer Vision Waste Segregation**:
       - Endpoint: `POST /api/classify-waste`
       - Detects item geometry and material using Ultralytics YOLOv8/v11.
       - Returns color-coded bin guidance: Green (Organic/Wet), Blue (Recyclable/Dry), Red (Hazardous).

    2. **Intelligent Collection Route Optimization**:
       - Endpoint: `POST /api/optimize-route`
       - Solves Vehicle Routing Problem (VRP) using Google OR-Tools & OSRM street network.
       - Compares standard full sweep vs AI smart path servicing only full bins (≥75%).
       - Delivers audit metrics: Distance Saved (km), Travel Time Saved (mins), Fuel Saved (L), CO₂ Avoided (kg).

    3. **IoT Smart Bin Telemetry & Analytics**:
       - Endpoints: `GET /api/bins`, `GET /api/analytics`
       - Simulates live sensor grid and historical efficiency benchmarks.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for Next.js frontend (Vercel, localhost, and public origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(classify_router, prefix=settings.API_PREFIX)
app.include_router(route_optimizer_router, prefix=settings.API_PREFIX)
app.include_router(bins_router, prefix=settings.API_PREFIX)

@app.get("/", tags=["System"])
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Online",
        "documentation": "/docs",
        "endpoints": {
            "classifyWaste": f"{settings.API_PREFIX}/classify-waste",
            "optimizeRoute": f"{settings.API_PREFIX}/optimize-route",
            "bins": f"{settings.API_PREFIX}/bins",
            "analytics": f"{settings.API_PREFIX}/analytics",
        },
    }

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "yoloModel": settings.YOLO_MODEL_PATH,
        "osrmBaseUrl": settings.OSRM_BASE_URL,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
