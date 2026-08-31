from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action, verify_chain

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("", response_model=schemas.CaseOut)
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(
        name=payload.name,
        description=payload.description,
        investigator=payload.investigator,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    log_action(db, case.id, "case_created", f"Case '{case.name}' created")
    return case


@router.get("", response_model=List[schemas.CaseOut])
def list_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).order_by(models.Case.created_at.desc()).all()


@router.get("/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: str, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case


@router.get("/{case_id}/audit-log", response_model=List[schemas.AuditLogOut])
def get_audit_log(case_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.AuditLog)
        .filter(models.AuditLog.case_id == case_id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )


@router.get("/{case_id}/audit-log/verify")
def verify_audit_log(case_id: str, db: Session = Depends(get_db)):
    """Recomputes the hash chain over the case's audit log and reports
    whether it's intact -- i.e. whether the chain-of-custody record has
    been tampered with since it was written."""
    return verify_chain(db, case_id)
