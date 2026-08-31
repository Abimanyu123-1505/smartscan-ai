import json
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/v1", tags=["graph"])


def _build_graph_from_case(db: Session, case_id: str):
    """Build entity graph nodes and edges from case data."""
    nodes = []
    edges = []
    node_map = {}  # label -> node_id

    def get_or_create_node(node_type: str, label: str, risk: float = 0.0, artifact_id: str = None):
        key = f"{node_type}:{label}"
        if key in node_map:
            return node_map[key]
        existing = db.query(models.GraphNode).filter(
            models.GraphNode.case_id == case_id,
            models.GraphNode.node_type == node_type,
            models.GraphNode.label == label
        ).first()
        if existing:
            node_map[key] = existing.id
            return existing.id
        node = models.GraphNode(
            case_id=case_id,
            node_type=node_type,
            label=label,
            risk_score=risk,
            artifact_id=artifact_id,
        )
        db.add(node)
        db.flush()
        node_map[key] = node.id
        return node.id

    def get_or_create_edge(src_id: str, tgt_id: str, edge_type: str):
        existing = db.query(models.GraphEdge).filter(
            models.GraphEdge.case_id == case_id,
            models.GraphEdge.source_node_id == src_id,
            models.GraphEdge.target_node_id == tgt_id,
            models.GraphEdge.edge_type == edge_type
        ).first()
        if not existing:
            edge = models.GraphEdge(
                case_id=case_id,
                source_node_id=src_id,
                target_node_id=tgt_id,
                edge_type=edge_type,
            )
            db.add(edge)

    # Add processes
    processes = db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.artifact_type == "process"
    ).all()
    for p in processes:
        risk = 80.0 if p.suspicious else 10.0
        proc_id = get_or_create_node("process", f"{p.name} (PID {p.pid})", risk)
        if p.ppid:
            parent = db.query(models.MemoryArtifact).filter(
                models.MemoryArtifact.case_id == case_id,
                models.MemoryArtifact.pid == p.ppid
            ).first()
            if parent:
                parent_id = get_or_create_node("process", f"{parent.name} (PID {parent.pid})")
                get_or_create_edge(parent_id, proc_id, "spawned")

    # Add network connections
    connections = db.query(models.NetworkArtifact).filter(
        models.NetworkArtifact.case_id == case_id
    ).all()
    for conn in connections:
        src_id = get_or_create_node("ip", conn.src_ip)
        if conn.hostname:
            domain_id = get_or_create_node("domain", conn.hostname, 80.0 if conn.flagged else 0.0)
            dst_id = get_or_create_node("ip", conn.dst_ip, 80.0 if conn.flagged else 0.0)
            get_or_create_edge(domain_id, dst_id, "resolves_to")
            get_or_create_edge(src_id, domain_id, "communicates_with")
        else:
            dst_id = get_or_create_node("ip", conn.dst_ip, 80.0 if conn.flagged else 0.0)
            get_or_create_edge(src_id, dst_id, "communicates_with")

    # Add registry flagged keys
    reg_keys = db.query(models.RegistryKey).filter(
        models.RegistryKey.case_id == case_id,
        models.RegistryKey.flagged == True
    ).all()
    for rk in reg_keys:
        reg_id = get_or_create_node("registry", rk.value_name, 70.0)
        if rk.value_data and ("exe" in rk.value_data.lower() or "dll" in rk.value_data.lower()):
            file_id = get_or_create_node("file", rk.value_data[:60], 70.0)
            get_or_create_edge(reg_id, file_id, "executes")

    db.commit()
    return db.query(models.GraphNode).filter(models.GraphNode.case_id == case_id).count()


@router.post("/cases/{case_id}/graph/build")
def build_graph(case_id: str, db: Session = Depends(get_db)):
    count = _build_graph_from_case(db, case_id)
    log_action(db, case_id, "graph_built", f"{count} nodes")
    return {"nodes_created": count}


@router.get("/cases/{case_id}/graph")
def get_graph(case_id: str, db: Session = Depends(get_db)):
    nodes = db.query(models.GraphNode).filter(models.GraphNode.case_id == case_id).all()
    edges = db.query(models.GraphEdge).filter(models.GraphEdge.case_id == case_id).all()
    return {
        "nodes": [{"id": n.id, "type": n.node_type, "label": n.label, "risk_score": n.risk_score, "artifact_id": n.artifact_id} for n in nodes],
        "edges": [{"id": e.id, "source": e.source_node_id, "target": e.target_node_id, "type": e.edge_type, "label": e.label} for e in edges],
    }
