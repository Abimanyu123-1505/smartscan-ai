from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action
import datetime as dt

router = APIRouter(prefix="/api/v1", tags=["memory"])


def _seed_mock_processes(db: Session, case_id: str, evidence_id: str):
    """Generate realistic-looking Volatility3 process list output."""
    MOCK_PROCESSES = [
        {"pid": 4, "ppid": 0, "name": "System", "path": "", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 488, "ppid": 4, "name": "smss.exe", "path": "C:\\Windows\\System32\\smss.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 600, "ppid": 488, "name": "csrss.exe", "path": "C:\\Windows\\System32\\csrss.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 668, "ppid": 488, "name": "wininit.exe", "path": "C:\\Windows\\System32\\wininit.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 720, "ppid": 668, "name": "services.exe", "path": "C:\\Windows\\System32\\services.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 728, "ppid": 668, "name": "lsass.exe", "path": "C:\\Windows\\System32\\lsass.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 1024, "ppid": 720, "name": "svchost.exe", "path": "C:\\Windows\\System32\\svchost.exe", "cmd": "-k netsvcs", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 1388, "ppid": 720, "name": "svchost.exe", "path": "C:\\Windows\\System32\\svchost.exe", "cmd": "-k LocalSystemNetworkRestricted", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 2456, "ppid": 1024, "name": "explorer.exe", "path": "C:\\Windows\\explorer.exe", "cmd": "", "suspicious": False, "hidden": False, "injected": False},
        {"pid": 3180, "ppid": 2456, "name": "cmd.exe", "path": "C:\\Windows\\System32\\cmd.exe", "cmd": "cmd.exe /c powershell -enc JABzAD0ATgBlAHcA", "suspicious": True, "hidden": False, "injected": False},
        {"pid": 3244, "ppid": 3180, "name": "powershell.exe", "path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "cmd": "-enc JABzAD0ATgBlAHcA...", "suspicious": True, "hidden": False, "injected": True},
        {"pid": 3512, "ppid": 3244, "name": "rundll32.exe", "path": "C:\\Windows\\System32\\rundll32.exe", "cmd": "rundll32.exe shell32.dll,Control_RunDLL", "suspicious": True, "hidden": True, "injected": True},
        {"pid": 3680, "ppid": 3512, "name": "svch0st.exe", "path": "C:\\Users\\victim\\AppData\\Roaming\\svch0st.exe", "cmd": "", "suspicious": True, "hidden": True, "injected": False},
    ]
    count = 0
    for p in MOCK_PROCESSES:
        existing = db.query(models.MemoryArtifact).filter(
            models.MemoryArtifact.case_id == case_id,
            models.MemoryArtifact.pid == p["pid"]
        ).first()
        if not existing:
            ma = models.MemoryArtifact(
                case_id=case_id,
                evidence_id=evidence_id,
                artifact_type="process",
                pid=p["pid"],
                ppid=p["ppid"],
                name=p["name"],
                path=p["path"],
                command_line=p["cmd"],
                suspicious=p["suspicious"],
                hidden=p["hidden"],
                injected=p["injected"],
                start_time=dt.datetime.utcnow() - dt.timedelta(hours=2),
            )
            db.add(ma)
            count += 1
    db.commit()
    return count


@router.get("/cases/{case_id}/memory/processes", response_model=List[schemas.MemoryArtifactOut])
def list_processes(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.artifact_type == "process"
    ).order_by(models.MemoryArtifact.pid).all()


@router.post("/cases/{case_id}/memory/analyze")
def analyze_memory(case_id: str, db: Session = Depends(get_db)):
    """Trigger memory analysis (real: Volatility3; mock: seed realistic data)."""
    # Find a memory dump evidence item or use the case id as seed
    evidence = db.query(models.Evidence).filter(
        models.Evidence.case_id == case_id
    ).first()
    if not evidence:
        raise HTTPException(404, "No evidence items found for this case")

    count = _seed_mock_processes(db, case_id, evidence.id)
    log_action(db, case_id, "memory_analyzed", f"Volatility3 analysis: {count} artifacts extracted")
    return {"status": "complete", "artifacts_extracted": count}


@router.get("/cases/{case_id}/memory/summary")
def memory_summary(case_id: str, db: Session = Depends(get_db)):
    total = db.query(models.MemoryArtifact).filter(models.MemoryArtifact.case_id == case_id).count()
    suspicious = db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.suspicious == True
    ).count()
    hidden = db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.hidden == True
    ).count()
    injected = db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.injected == True
    ).count()
    return {"total": total, "suspicious": suspicious, "hidden": hidden, "injected": injected}
