import json
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/v1", tags=["ioc"])


@router.get("/cases/{case_id}/iocs", response_model=List[schemas.IOCOut])
def list_iocs(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.IOC).filter(models.IOC.case_id == case_id).order_by(models.IOC.created_at.desc()).all()


@router.post("/cases/{case_id}/iocs", response_model=schemas.IOCOut)
def create_ioc(case_id: str, payload: schemas.IOCCreate, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    ioc = models.IOC(
        case_id=case_id,
        ioc_type=payload.ioc_type,
        value=payload.value,
        description=payload.description,
        source=payload.source,
        risk_score=payload.risk_score,
        tags_json=json.dumps(payload.tags),
    )
    db.add(ioc)
    db.commit()
    db.refresh(ioc)
    log_action(db, case_id, "ioc_added", f"{payload.ioc_type}: {payload.value}")
    return ioc


@router.post("/cases/{case_id}/iocs/scan")
def scan_iocs(case_id: str, db: Session = Depends(get_db)):
    """Scan all artifacts in the case against all IOCs."""
    iocs = db.query(models.IOC).filter(models.IOC.case_id == case_id).all()
    artifacts = db.query(models.Artifact).filter(models.Artifact.case_id == case_id).all()
    matches_created = 0
    for ioc in iocs:
        for artifact in artifacts:
            # Check if IOC value appears in artifact fields
            searchable = f"{artifact.name} {artifact.path} {artifact.extra_json}"
            if ioc.value.lower() in searchable.lower():
                # Check not already matched
                existing = db.query(models.IOCMatch).filter(
                    models.IOCMatch.ioc_id == ioc.id,
                    models.IOCMatch.artifact_id == artifact.id
                ).first()
                if not existing:
                    match = models.IOCMatch(
                        ioc_id=ioc.id,
                        artifact_id=artifact.id,
                        case_id=case_id,
                        match_context=f"Found in {artifact.artifact_type}: {artifact.name}"
                    )
                    db.add(match)
                    matches_created += 1
    db.commit()
    log_action(db, case_id, "ioc_scan", f"Scanned {len(artifacts)} artifacts, {matches_created} new matches")
    return {"matches_created": matches_created, "iocs_scanned": len(iocs), "artifacts_scanned": len(artifacts)}


@router.get("/cases/{case_id}/ioc-matches", response_model=List[schemas.IOCMatchOut])
def list_ioc_matches(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.IOCMatch).filter(models.IOCMatch.case_id == case_id).order_by(models.IOCMatch.matched_at.desc()).all()


@router.delete("/cases/{case_id}/iocs/{ioc_id}")
def delete_ioc(case_id: str, ioc_id: str, db: Session = Depends(get_db)):
    ioc = db.query(models.IOC).filter(models.IOC.id == ioc_id, models.IOC.case_id == case_id).first()
    if not ioc:
        raise HTTPException(404, "IOC not found")
    db.delete(ioc)
    db.commit()
    return {"deleted": ioc_id}
