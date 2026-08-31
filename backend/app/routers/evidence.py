import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db, DATA_DIR
from ..services.hashing import hash_file
from ..services.acquisition import run_parsers_on_evidence
from ..services.audit import log_action

router = APIRouter(prefix="/api", tags=["evidence"])

EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


@router.post("/cases/{case_id}/evidence", response_model=schemas.EvidenceOut)
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    evidence_type: str = Form("filesystem_bundle"),
    acquired_by: str = Form("analyst"),
    db: Session = Depends(get_db),
):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    case_dir = os.path.join(EVIDENCE_DIR, case_id)
    os.makedirs(case_dir, exist_ok=True)
    dest_path = os.path.join(case_dir, file.filename)

    # Acquisition: original bytes are written once, then never opened for
    # writing again. All downstream parsing works on copies (see plugins).
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    os.chmod(dest_path, 0o444)  # read-only, mirrors write-blocking a real image

    digest = hash_file(dest_path)

    evidence = models.Evidence(
        case_id=case_id,
        original_filename=file.filename,
        stored_path=dest_path,
        evidence_type=evidence_type,
        size_bytes=digest["size_bytes"],
        sha256=digest["sha256"],
        sha1=digest["sha1"],
        md5=digest["md5"],
        acquired_by=acquired_by,
        verification_ok="ok",
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    log_action(
        db, case_id, "evidence_acquired",
        f"{file.filename} ({digest['size_bytes']} bytes, sha256={digest['sha256'][:12]}…)",
        actor=acquired_by,
    )

    created = run_parsers_on_evidence(db, evidence)
    log_action(
        db, case_id, "evidence_parsed",
        f"{file.filename}: {created} artifact(s) extracted",
        actor="system",
    )

    return evidence


@router.get("/cases/{case_id}/evidence", response_model=List[schemas.EvidenceOut])
def list_evidence(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()


@router.post("/evidence/{evidence_id}/verify", response_model=schemas.EvidenceOut)
def reverify_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """Cryptographic Verification control: re-hash the stored file and
    confirm it still matches the value recorded at acquisition time."""
    import datetime as dt

    evidence = db.get(models.Evidence, evidence_id)
    if not evidence:
        raise HTTPException(404, "Evidence not found")

    digest = hash_file(evidence.stored_path)
    evidence.verification_ok = "ok" if digest["sha256"] == evidence.sha256 else "mismatch"
    evidence.verified_at = dt.datetime.utcnow()
    db.commit()
    db.refresh(evidence)

    log_action(
        db, evidence.case_id, "evidence_reverified",
        f"{evidence.original_filename}: {evidence.verification_ok}",
        actor="system",
    )
    return evidence
