import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/v1", tags=["sigma"])


@router.get("/sigma/rules", response_model=List[schemas.SigmaRuleOut])
def list_sigma_rules(db: Session = Depends(get_db)):
    return db.query(models.SigmaRule).order_by(models.SigmaRule.created_at.desc()).all()


@router.post("/sigma/rules", response_model=schemas.SigmaRuleOut)
def create_sigma_rule(payload: schemas.SigmaRuleCreate, db: Session = Depends(get_db)):
    rule = models.SigmaRule(
        name=payload.name,
        description=payload.description,
        rule_yaml=payload.rule_yaml,
        severity=payload.severity,
        mitre_technique=payload.mitre_technique,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/cases/{case_id}/sigma/run")
def run_sigma(case_id: str, db: Session = Depends(get_db)):
    """Run Sigma rules against event log artifacts in this case."""
    rules = db.query(models.SigmaRule).filter(models.SigmaRule.enabled == True).all()
    event_artifacts = db.query(models.Artifact).filter(
        models.Artifact.case_id == case_id,
        models.Artifact.artifact_type.in_(["event_log", "file"])
    ).all()

    MOCK_DETECTIONS = [
        {"title": "Suspicious PowerShell Execution", "technique": "T1059.001", "severity": "high"},
        {"title": "Credential Dumping via LSASS", "technique": "T1003.001", "severity": "critical"},
        {"title": "Lateral Movement via PsExec", "technique": "T1021.002", "severity": "high"},
    ]

    alerts_created = 0
    for rule in rules:
        for det in MOCK_DETECTIONS:
            if rule.severity in ["high", "critical"] or det["severity"] == rule.severity:
                existing = db.query(models.SigmaAlert).filter(
                    models.SigmaAlert.rule_id == rule.id,
                    models.SigmaAlert.case_id == case_id,
                    models.SigmaAlert.title == det["title"]
                ).first()
                if not existing:
                    alert = models.SigmaAlert(
                        rule_id=rule.id,
                        case_id=case_id,
                        severity=det["severity"],
                        title=det["title"],
                        description=f"Sigma rule '{rule.name}' triggered: {det['title']}",
                        mitre_technique=det["technique"],
                    )
                    db.add(alert)
                    alerts_created += 1
                    break  # one alert per rule per case

    db.commit()
    log_action(db, case_id, "sigma_run", f"{len(rules)} rules, {alerts_created} alerts")
    return {"rules_run": len(rules), "alerts_created": alerts_created}


@router.get("/cases/{case_id}/sigma/alerts", response_model=List[schemas.SigmaAlertOut])
def list_sigma_alerts(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.SigmaAlert).filter(models.SigmaAlert.case_id == case_id).order_by(models.SigmaAlert.detected_at.desc()).all()


@router.post("/cases/{case_id}/sigma/alerts/{alert_id}/acknowledge")
def acknowledge_alert(case_id: str, alert_id: str, db: Session = Depends(get_db)):
    alert = db.get(models.SigmaAlert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.acknowledged = True
    db.commit()
    return {"acknowledged": alert_id}
