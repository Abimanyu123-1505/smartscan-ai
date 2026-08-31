from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, init_fts_index
from .routers import cases, evidence, artifacts, search, reports
from .routers.artifacts import artifact_router
from .routers import dashboard, ioc, yara, sigma, mitre, memory, network, registry, malware, ai, graph

Base.metadata.create_all(bind=engine)
init_fts_index()

app = FastAPI(
    title="DFIOP — Digital Forensics Investigation Operating Platform",
    description=(
        "Production-grade digital forensics platform supporting Case Management, "
        "Evidence Acquisition, Disk/Memory/Network/Registry Forensics, "
        "IOC Hunting, YARA/Sigma Detection, MITRE ATT&CK Mapping, "
        "Malware Analysis, Entity Graph, AI Assistant, and Chain-of-Custody Reporting."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Phase 1 core routers ──────────────────────────────────────────────────────
app.include_router(cases.router)
app.include_router(evidence.router)
app.include_router(artifacts.router)
app.include_router(artifact_router)
app.include_router(search.router)
app.include_router(reports.router)

# ── Phase 2 enterprise routers ────────────────────────────────────────────────
app.include_router(dashboard.router)
app.include_router(ioc.router)
app.include_router(yara.router)
app.include_router(sigma.router)
app.include_router(mitre.router)
app.include_router(memory.router)
app.include_router(network.router)
app.include_router(registry.router)
app.include_router(malware.router)
app.include_router(ai.router)
app.include_router(graph.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "platform": "DFIOP", "version": "2.0.0"}
