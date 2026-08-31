import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/cases", tags=["artifacts"])
artifact_router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])


@router.get("/{case_id}/artifacts", response_model=List[schemas.ArtifactOut])
def list_artifacts(
    case_id: str,
    artifact_type: Optional[str] = None,
    limit: int = Query(500, le=5000),
    db: Session = Depends(get_db),
):
    q = db.query(models.Artifact).filter(models.Artifact.case_id == case_id)
    if artifact_type:
        q = q.filter(models.Artifact.artifact_type == artifact_type)
    return q.order_by(models.Artifact.modified_ts.desc()).limit(limit).all()


@router.get("/{case_id}/timeline", response_model=List[schemas.TimelineEventOut])
def get_timeline(
    case_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(1000, le=10000),
    db: Session = Depends(get_db),
):
    q = db.query(models.TimelineEvent).filter(models.TimelineEvent.case_id == case_id)
    if start:
        q = q.filter(models.TimelineEvent.event_ts >= start)
    if end:
        q = q.filter(models.TimelineEvent.event_ts <= end)
    if event_type:
        q = q.filter(models.TimelineEvent.event_type == event_type)
    return q.order_by(models.TimelineEvent.event_ts.desc()).limit(limit).all()


@artifact_router.post("/{artifact_id}/label", response_model=schemas.ArtifactOut)
def add_label(artifact_id: str, payload: schemas.LabelUpdate, db: Session = Depends(get_db)):
    """Human-in-the-loop confirmation, per the roadmap's 'AI/heuristic
    suggests, analyst verifies' principle: adds a label (e.g.
    'verified', 'false-positive') to an artifact. A 'verified' label
    also raises confidence to 1.0, since it's now analyst-confirmed
    rather than only heuristically flagged."""
    artifact = db.get(models.Artifact, artifact_id)
    if not artifact:
        raise HTTPException(404, "Artifact not found")

    labels = json.loads(artifact.labels_json or "[]")
    if payload.label not in labels:
        labels.append(payload.label)
    artifact.labels_json = json.dumps(labels)
    if payload.label == "verified":
        artifact.confidence = 1.0
    db.commit()
    db.refresh(artifact)

    log_action(
        db, artifact.case_id, "artifact_labeled",
        f"{artifact.name}: +'{payload.label}'" + (f" by {payload.verified_by}" if payload.verified_by else ""),
        actor=payload.verified_by or "analyst",
    )
    return artifact
