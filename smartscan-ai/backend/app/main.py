from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import (
    health, datasets, simulation, replay,
    receiver, prediction, intelligence, policies,
    experiments, benchmarks, reports
)
from api.websocket import router as ws_router

app = FastAPI(title="SmartScan-AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(replay.router, prefix="/api/replay", tags=["replay"])
app.include_router(receiver.router, prefix="/api/receiver", tags=["receiver"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])
app.include_router(policies.router, prefix="/api/policies", tags=["policies"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(benchmarks.router, prefix="/api/benchmarks", tags=["benchmarks"])
from app.api import routes_ml_eval, routes_research_labs

app.include_router(routes_ml_eval.router)
app.include_router(routes_research_labs.router)
app.include_router(ws_router)

@app.on_event("startup")
async def startup_event():
    print("Starting up SmartScan-AI backend...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
