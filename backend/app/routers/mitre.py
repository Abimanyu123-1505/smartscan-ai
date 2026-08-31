from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/v1", tags=["mitre"])

# Full MITRE ATT&CK matrix data (representative techniques)
MITRE_TACTICS = [
    {"id": "TA0001", "name": "Initial Access", "techniques": [
        {"id": "T1566", "name": "Phishing", "sub": ["T1566.001", "T1566.002", "T1566.003"]},
        {"id": "T1190", "name": "Exploit Public-Facing Application", "sub": []},
        {"id": "T1133", "name": "External Remote Services", "sub": []},
        {"id": "T1078", "name": "Valid Accounts", "sub": ["T1078.001", "T1078.002", "T1078.003"]},
    ]},
    {"id": "TA0002", "name": "Execution", "techniques": [
        {"id": "T1059", "name": "Command and Scripting Interpreter", "sub": ["T1059.001", "T1059.003", "T1059.005"]},
        {"id": "T1203", "name": "Exploitation for Client Execution", "sub": []},
        {"id": "T1053", "name": "Scheduled Task/Job", "sub": ["T1053.005"]},
        {"id": "T1569", "name": "System Services", "sub": ["T1569.002"]},
    ]},
    {"id": "TA0003", "name": "Persistence", "techniques": [
        {"id": "T1547", "name": "Boot or Logon Autostart Execution", "sub": ["T1547.001"]},
        {"id": "T1543", "name": "Create or Modify System Process", "sub": ["T1543.003"]},
        {"id": "T1136", "name": "Create Account", "sub": ["T1136.001", "T1136.002"]},
        {"id": "T1574", "name": "Hijack Execution Flow", "sub": ["T1574.001", "T1574.002"]},
    ]},
    {"id": "TA0004", "name": "Privilege Escalation", "techniques": [
        {"id": "T1548", "name": "Abuse Elevation Control Mechanism", "sub": ["T1548.002"]},
        {"id": "T1134", "name": "Access Token Manipulation", "sub": []},
        {"id": "T1055", "name": "Process Injection", "sub": ["T1055.001", "T1055.002"]},
        {"id": "T1068", "name": "Exploitation for Privilege Escalation", "sub": []},
    ]},
    {"id": "TA0005", "name": "Defense Evasion", "techniques": [
        {"id": "T1070", "name": "Indicator Removal", "sub": ["T1070.001", "T1070.004"]},
        {"id": "T1036", "name": "Masquerading", "sub": ["T1036.003", "T1036.005"]},
        {"id": "T1027", "name": "Obfuscated Files or Information", "sub": []},
        {"id": "T1562", "name": "Impair Defenses", "sub": ["T1562.001"]},
    ]},
    {"id": "TA0006", "name": "Credential Access", "techniques": [
        {"id": "T1003", "name": "OS Credential Dumping", "sub": ["T1003.001", "T1003.002"]},
        {"id": "T1110", "name": "Brute Force", "sub": ["T1110.001", "T1110.003"]},
        {"id": "T1555", "name": "Credentials from Password Stores", "sub": ["T1555.003"]},
        {"id": "T1552", "name": "Unsecured Credentials", "sub": ["T1552.001"]},
    ]},
    {"id": "TA0007", "name": "Discovery", "techniques": [
        {"id": "T1082", "name": "System Information Discovery", "sub": []},
        {"id": "T1083", "name": "File and Directory Discovery", "sub": []},
        {"id": "T1057", "name": "Process Discovery", "sub": []},
        {"id": "T1046", "name": "Network Service Scanning", "sub": []},
    ]},
    {"id": "TA0008", "name": "Lateral Movement", "techniques": [
        {"id": "T1021", "name": "Remote Services", "sub": ["T1021.001", "T1021.002", "T1021.006"]},
        {"id": "T1210", "name": "Exploitation of Remote Services", "sub": []},
        {"id": "T1534", "name": "Internal Spearphishing", "sub": []},
    ]},
    {"id": "TA0009", "name": "Collection", "techniques": [
        {"id": "T1560", "name": "Archive Collected Data", "sub": ["T1560.001"]},
        {"id": "T1056", "name": "Input Capture", "sub": ["T1056.001"]},
        {"id": "T1113", "name": "Screen Capture", "sub": []},
        {"id": "T1005", "name": "Data from Local System", "sub": []},
    ]},
    {"id": "TA0010", "name": "Exfiltration", "techniques": [
        {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "sub": []},
        {"id": "T1041", "name": "Exfiltration Over C2 Channel", "sub": []},
        {"id": "T1567", "name": "Exfiltration Over Web Service", "sub": ["T1567.002"]},
    ]},
    {"id": "TA0011", "name": "Command and Control", "techniques": [
        {"id": "T1071", "name": "Application Layer Protocol", "sub": ["T1071.001", "T1071.004"]},
        {"id": "T1105", "name": "Ingress Tool Transfer", "sub": []},
        {"id": "T1573", "name": "Encrypted Channel", "sub": ["T1573.001", "T1573.002"]},
    ]},
    {"id": "TA0040", "name": "Impact", "techniques": [
        {"id": "T1486", "name": "Data Encrypted for Impact", "sub": []},
        {"id": "T1490", "name": "Inhibit System Recovery", "sub": []},
        {"id": "T1489", "name": "Service Stop", "sub": []},
        {"id": "T1485", "name": "Data Destruction", "sub": []},
    ]},
]


@router.get("/mitre/matrix")
def get_matrix():
    """Return the full MITRE ATT&CK matrix structure."""
    return {"tactics": MITRE_TACTICS}


@router.get("/cases/{case_id}/mitre/mappings", response_model=List[schemas.MITREMappingOut])
def list_mappings(case_id: str, db: Session = Depends(get_db)):
    return db.query(models.MITREMapping).filter(models.MITREMapping.case_id == case_id).all()


@router.get("/cases/{case_id}/mitre/heatmap")
def get_heatmap(case_id: str, db: Session = Depends(get_db)):
    """Return technique hit counts for the ATT&CK navigator heatmap."""
    mappings = db.query(models.MITREMapping).filter(models.MITREMapping.case_id == case_id).all()
    # Also pull from sigma alerts
    alerts = db.query(models.SigmaAlert).filter(models.SigmaAlert.case_id == case_id).all()

    from collections import defaultdict
    counts = defaultdict(int)
    for m in mappings:
        if m.technique_id:
            counts[m.technique_id] += 1
    for a in alerts:
        if a.mitre_technique:
            counts[a.mitre_technique] += 1

    return {"heatmap": [{"technique_id": k, "count": v} for k, v in counts.items()]}
