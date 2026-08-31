"""
SmartScan AI — Backend API
Milestone 1: Real-data ingestion, replay, evaluation

Run with:
    cd smartscan/backend
    uvicorn main:app --reload --port 8001

Note: This runs on port 8001 to avoid conflict with DFIOP on port 8000.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from api.routes_data import router as data_router
from api.routes_replay import router as replay_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SmartScan AI API",
    version="1.0.0-milestone1",
    description="Backend API for SmartScan AI"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(data_router)
app.include_router(replay_router)

# Static files
SAMPLES_DIR = Path(__file__).parent.parent / "data" / "samples"
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")

@app.on_event("startup")
async def startup_event():
    logger.info("SmartScan AI backend starting on port 8001")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
