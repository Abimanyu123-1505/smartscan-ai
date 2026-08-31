from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action
import datetime as dt

router = APIRouter(prefix="/api/v1", tags=["network"])

MOCK_CONNECTIONS = [
    {"proto": "HTTPS", "src_ip": "192.168.1.45", "src_port": 52341, "dst_ip": "185.199.108.153", "dst_port": 443, "host": "raw.githubusercontent.com", "bytes_s": 1240, "bytes_r": 48320, "sni": "raw.githubusercontent.com", "flagged": False, "flag_reason": ""},
    {"proto": "DNS", "src_ip": "192.168.1.45", "src_port": 53421, "dst_ip": "8.8.8.8", "dst_port": 53, "host": "", "bytes_s": 64, "bytes_r": 128, "sni": "", "flagged": False, "flag_reason": ""},
    {"proto": "HTTP", "src_ip": "192.168.1.45", "src_port": 54001, "dst_ip": "45.33.32.156", "dst_port": 80, "host": "c2server-dga.xyz", "bytes_s": 340, "bytes_r": 8920, "sni": "", "flagged": True, "flag_reason": "DGA-pattern domain; potential C2"},
    {"proto": "TLS", "src_ip": "192.168.1.45", "src_port": 55210, "dst_ip": "10.0.0.200", "dst_port": 4444, "host": "", "bytes_s": 12400, "bytes_r": 3200, "sni": "", "flagged": True, "flag_reason": "Non-standard port TLS; possible reverse shell"},
    {"proto": "SMB", "src_ip": "192.168.1.45", "src_port": 49155, "dst_ip": "192.168.1.10", "dst_port": 445, "host": "DC01", "bytes_s": 5400, "bytes_r": 23000, "sni": "", "flagged": False, "flag_reason": ""},
    {"proto": "DNS", "src_ip": "192.168.1.45", "src_port": 53433, "dst_ip": "8.8.8.8", "dst_port": 53, "host": "", "bytes_s": 72, "bytes_r": 72, "sni": "", "flagged": True, "flag_reason": "DNS query for known malware C2: c2server-dga.xyz"},
    {"proto": "HTTPS", "src_ip": "192.168.1.45", "src_port": 56001, "dst_ip": "13.107.42.16", "dst_port": 443, "host": "outlook.office365.com", "bytes_s": 2100, "bytes_r": 18700, "sni": "outlook.office365.com", "flagged": False, "flag_reason": ""},
    {"proto": "FTP", "src_ip": "192.168.1.45", "src_port": 57210, "dst_ip": "194.165.16.32", "dst_port": 21, "host": "", "bytes_s": 245000, "bytes_r": 1200, "sni": "", "flagged": True, "flag_reason": "Large FTP upload to external IP; possible data exfiltration"},
]


def _seed_network(db: Session, case_id: str, evidence_id: str):
    count = 0
    base_time = dt.datetime.utcnow() - dt.timedelta(hours=3)
    for i, conn in enumerate(MOCK_CONNECTIONS):
        existing = db.query(models.NetworkArtifact).filter(
            models.NetworkArtifact.case_id == case_id,
            models.NetworkArtifact.dst_ip == conn["dst_ip"],
            models.NetworkArtifact.protocol == conn["proto"]
        ).first()
        if not existing:
            na = models.NetworkArtifact(
                case_id=case_id,
                evidence_id=evidence_id,
                protocol=conn["proto"],
                src_ip=conn["src_ip"],
                src_port=conn["src_port"],
                dst_ip=conn["dst_ip"],
                dst_port=conn["dst_port"],
                hostname=conn["host"],
                bytes_sent=conn["bytes_s"],
                bytes_recv=conn["bytes_r"],
                tls_sni=conn["sni"],
                dns_query=conn["host"] if conn["proto"] == "DNS" else "",
                timestamp=base_time + dt.timedelta(minutes=i * 5),
                flagged=conn["flagged"],
                flag_reason=conn["flag_reason"],
            )
            db.add(na)
            count += 1
    db.commit()
    return count


@router.post("/cases/{case_id}/network/analyze")
def analyze_network(case_id: str, db: Session = Depends(get_db)):
    evidence = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).first()
    if not evidence:
        from fastapi import HTTPException
        raise HTTPException(404, "No evidence found")
    count = _seed_network(db, case_id, evidence.id)
    log_action(db, case_id, "network_analyzed", f"{count} connections extracted")
    return {"status": "complete", "connections": count}


@router.get("/cases/{case_id}/network/connections", response_model=List[schemas.NetworkArtifactOut])
def list_connections(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.NetworkArtifact).filter(models.NetworkArtifact.case_id == case_id).order_by(models.NetworkArtifact.timestamp.desc()).all()


@router.get("/cases/{case_id}/network/summary")
def network_summary(case_id: str, db: Session = Depends(get_db)):
    total = db.query(models.NetworkArtifact).filter(models.NetworkArtifact.case_id == case_id).count()
    flagged = db.query(models.NetworkArtifact).filter(
        models.NetworkArtifact.case_id == case_id, models.NetworkArtifact.flagged == True
    ).count()
    from sqlalchemy import func
    protos = db.query(
        models.NetworkArtifact.protocol, func.count(models.NetworkArtifact.id)
    ).filter(models.NetworkArtifact.case_id == case_id).group_by(models.NetworkArtifact.protocol).all()
    return {"total": total, "flagged": flagged, "protocols": [{"protocol": p[0], "count": p[1]} for p in protos]}
