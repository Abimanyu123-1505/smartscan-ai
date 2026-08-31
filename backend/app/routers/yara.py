import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/v1", tags=["yara"])


@router.get("/yara/rules", response_model=List[schemas.YARARuleOut])
def list_rules(db: Session = Depends(get_db)):
    return db.query(models.YARARule).order_by(models.YARARule.created_at.desc()).all()


@router.post("/yara/rules", response_model=schemas.YARARuleOut)
def create_rule(payload: schemas.YARARuleCreate, db: Session = Depends(get_db)):
    rule = models.YARARule(
        name=payload.name,
        description=payload.description,
        rule_text=payload.rule_text,
        author=payload.author,
        tags_json=json.dumps(payload.tags),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/cases/{case_id}/yara/scan")
def scan_case(case_id: str, db: Session = Depends(get_db)):
    """Run all enabled YARA rules against case artifacts.
    In production, this calls yara-python against stored evidence files.
    Here we provide realistic mock results for files whose names match
    common malware indicators."""
    rules = db.query(models.YARARule).filter(models.YARARule.enabled == True).all()
    artifacts = db.query(models.Artifact).filter(
        models.Artifact.case_id == case_id,
        models.Artifact.artifact_type == "file"
    ).all()

    SUSPICIOUS_EXTENSIONS = {".exe", ".dll", ".ps1", ".bat", ".vbs", ".js", ".hta"}
    matches_created = 0

    for artifact in artifacts:
        import os
        ext = os.path.splitext(artifact.name)[1].lower()
        if ext not in SUSPICIOUS_EXTENSIONS:
            continue
        for rule in rules:
            existing = db.query(models.YARAMatch).filter(
                models.YARAMatch.rule_id == rule.id,
                models.YARAMatch.file_path == artifact.path
            ).first()
            if not existing:
                match = models.YARAMatch(
                    rule_id=rule.id,
                    case_id=case_id,
                    artifact_id=artifact.id,
                    file_path=artifact.path,
                    matched_strings_json=json.dumps([
                        {"name": "$suspicious", "offset": 0, "data": "<simulated match>"}
                    ])
                )
                db.add(match)
                rule.match_count = (rule.match_count or 0) + 1
                matches_created += 1

    db.commit()
    log_action(db, case_id, "yara_scan", f"{len(rules)} rules, {matches_created} matches")
    return {"rules_run": len(rules), "files_scanned": len(artifacts), "matches": matches_created}


@router.get("/cases/{case_id}/yara/matches", response_model=List[schemas.YARAMatchOut])
def list_matches(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.YARAMatch).filter(models.YARAMatch.case_id == case_id).order_by(models.YARAMatch.matched_at.desc()).all()


@router.delete("/yara/rules/{rule_id}")
def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    rule = db.get(models.YARARule, rule_id)
    if not rule:
        raise HTTPException(404, "Rule not found")
    db.delete(rule)
    db.commit()
    return {"deleted": rule_id}
