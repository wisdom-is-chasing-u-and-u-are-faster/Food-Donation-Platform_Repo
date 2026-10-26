import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.db.init_db import init_database
from app.api import api_router

# Ensure database is initialized upon module load
init_database()

app = FastAPI(
    title="Enterprise Food Donation & Cloud-Native Logistics Mesh Platform",
    description="High-performance cloud-native logistics mesh for surplus food rescue with HACCP thermal telemetry, PostGIS geospatial matching, dual-fleet dispatch, and cryptographic chain-of-custody ledger.",
    version="1.0.0"
)

# CORS Middleware with configurable environment origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event: ensure DB schema and seed data
@app.on_event("startup")
def on_startup():
    init_database()

# Health and readiness probe
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "food-donation-platform",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# Register API routes
app.include_router(api_router)

# Mount static frontend directory and HTML pages
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if not os.path.exists(public_dir):
    public_dir = "public"

if os.path.exists(public_dir):
    pages_dir = os.path.join(public_dir, "pages")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir, html=True), name="pages")
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
