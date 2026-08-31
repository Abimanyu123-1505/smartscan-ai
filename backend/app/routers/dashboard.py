from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
import os

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    open_cases = db.query(func.count(models.Case.id)).filter(models.Case.status.in_(["open", "active"])).scalar() or 0
    closed_cases = db.query(func.count(models.Case.id)).filter(models.Case.status == "closed").scalar() or 0
    total_evidence = db.query(func.count(models.Evidence.id)).scalar() or 0
    total_artifacts = db.query(func.count(models.Artifact.id)).scalar() or 0
    timeline_events = db.query(func.count(models.TimelineEvent.id)).scalar() or 0
    malware_found = db.query(func.count(models.MalwareSample.id)).scalar() or 0
    high_risk_cases = db.query(func.count(models.Case.id)).filter(models.Case.risk_score >= 70).scalar() or 0
    ioc_hits = db.query(func.count(models.IOCMatch.id)).scalar() or 0
    yara_matches = db.query(func.count(models.YARAMatch.id)).scalar() or 0
    sigma_alerts = db.query(func.count(models.SigmaAlert.id)).scalar() or 0

    # Calculate storage used
    storage_used_mb = 0.0
    evidence_items = db.query(models.Evidence).all()
    for ev in evidence_items:
        storage_used_mb += ev.size_bytes / (1024 * 1024)

    return schemas.DashboardStats(
        open_cases=open_cases,
        closed_cases=closed_cases,
        total_evidence=total_evidence,
        total_artifacts=total_artifacts,
        timeline_events=timeline_events,
        malware_found=malware_found,
        high_risk_cases=high_risk_cases,
        storage_used_mb=round(storage_used_mb, 2),
        ioc_hits=ioc_hits,
        yara_matches=yara_matches,
        sigma_alerts=sigma_alerts,
    )


@router.get("/dashboard/case-trend")
def get_case_trend(db: Session = Depends(get_db)):
    """Returns case creation counts grouped by day for the last 30 days."""
    cases = db.query(models.Case).order_by(models.Case.created_at.desc()).limit(200).all()
    from collections import defaultdict
    trend = defaultdict(int)
    for c in cases:
        day = c.created_at.strftime("%Y-%m-%d")
        trend[day] += 1
    return {"trend": [{ "date": k, "count": v } for k, v in sorted(trend.items())]}


@router.get("/dashboard/evidence-types")
def get_evidence_types(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = db.query(
        models.Evidence.evidence_type,
        func.count(models.Evidence.id).label("count")
    ).group_by(models.Evidence.evidence_type).all()
    return {"types": [{"type": r[0], "count": r[1]} for r in rows]}


@router.get("/dashboard/artifact-types")
def get_artifact_types(db: Session = Depends(get_db)):
    from sqlalchemy import func
    rows = db.query(
        models.Artifact.artifact_type,
        func.count(models.Artifact.id).label("count")
    ).group_by(models.Artifact.artifact_type).all()
    return {"types": [{"type": r[0], "count": r[1]} for r in rows]}


@router.get("/dashboard/recent-activity")
def get_recent_activity(db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(20).all()
    return {"activity": [{
        "actor": l.actor,
        "action": l.action,
        "detail": l.detail,
        "timestamp": l.timestamp.isoformat()
    } for l in logs]}
