from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action
import datetime as dt

router = APIRouter(prefix="/api/v1", tags=["registry"])

MOCK_REGISTRY_KEYS = [
    {"hive": "NTUSER.DAT", "path": "Software\\Microsoft\\Windows\\CurrentVersion\\Run", "name": "Updater", "type": "REG_SZ", "data": "C:\\Users\\victim\\AppData\\Roaming\\svch0st.exe", "cat": "run_key", "flagged": True, "reason": "Non-standard executable in Run key"},
    {"hive": "SOFTWARE", "path": "Microsoft\\Windows\\CurrentVersion\\Run", "name": "SecurityHealth", "type": "REG_SZ", "data": "%windir%\\system32\\SecurityHealth.exe", "cat": "run_key", "flagged": False, "reason": ""},
    {"hive": "SYSTEM", "path": "CurrentControlSet\\Services\\SuspiciousSvc", "name": "ImagePath", "type": "REG_EXPAND_SZ", "data": "C:\\Windows\\Temp\\malware.exe", "cat": "run_key", "flagged": True, "reason": "Service binary in %TEMP%"},
    {"hive": "SAM", "path": "SAM\\Domains\\Account\\Users", "name": "Administrator", "type": "REG_BINARY", "data": "<binary>", "cat": "user_accounts", "flagged": False, "reason": ""},
    {"hive": "SYSTEM", "path": "CurrentControlSet\\Enum\\USBSTOR", "name": "Disk&Ven_SanDisk&Prod_Cruzer", "type": "REG_SZ", "data": "SanDisk Cruzer 16GB", "cat": "usb", "flagged": False, "reason": ""},
    {"hive": "SYSTEM", "path": "CurrentControlSet\\Enum\\USBSTOR", "name": "Disk&Ven_Unknown", "type": "REG_SZ", "data": "Unknown Device", "cat": "usb", "flagged": True, "reason": "Unrecognized USB device"},
    {"hive": "NTUSER.DAT", "path": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs", "name": "MRU", "type": "REG_BINARY", "data": "financials_2024.xlsx; passwords.txt; exfil_archive.zip", "cat": "mru", "flagged": True, "reason": "Suspicious filenames in MRU"},
    {"hive": "NTUSER.DAT", "path": "Software\\Microsoft\\Windows\\ShellNoRoam\\BagMRU", "name": "0", "type": "REG_BINARY", "data": "C:\\Users\\victim\\Desktop\\exfil_archive.zip", "cat": "shellbag", "flagged": True, "reason": "Shellbag entry for suspicious archive"},
    {"hive": "SOFTWARE", "path": "Microsoft\\Windows NT\\CurrentVersion", "name": "CurrentVersion", "type": "REG_SZ", "data": "10.0", "cat": "system_info", "flagged": False, "reason": ""},
    {"hive": "SYSTEM", "path": "CurrentControlSet\\Control\\TimeZoneInformation", "name": "TimeZoneKeyName", "type": "REG_SZ", "data": "Eastern Standard Time", "cat": "timezone", "flagged": False, "reason": ""},
    {"hive": "SOFTWARE", "path": "Microsoft\\Windows\\CurrentVersion\\Uninstall\\7-Zip", "name": "DisplayName", "type": "REG_SZ", "data": "7-Zip 23.01", "cat": "installed_app", "flagged": False, "reason": ""},
    {"hive": "SOFTWARE", "path": "Microsoft\\Windows\\CurrentVersion\\Uninstall\\Mimikatz", "name": "DisplayName", "type": "REG_SZ", "data": "Mimikatz 2.2.0", "cat": "installed_app", "flagged": True, "reason": "Credential harvesting tool detected"},
]


def _seed_registry(db: Session, case_id: str, evidence_id: str):
    count = 0
    base_ts = dt.datetime.utcnow() - dt.timedelta(days=7)
    for i, key in enumerate(MOCK_REGISTRY_KEYS):
        existing = db.query(models.RegistryKey).filter(
            models.RegistryKey.case_id == case_id,
            models.RegistryKey.key_path == key["path"],
            models.RegistryKey.value_name == key["name"]
        ).first()
        if not existing:
            rk = models.RegistryKey(
                case_id=case_id,
                evidence_id=evidence_id,
                hive=key["hive"],
                key_path=key["path"],
                value_name=key["name"],
                value_type=key["type"],
                value_data=key["data"],
                last_modified=base_ts + dt.timedelta(hours=i * 6),
                category=key["cat"],
                flagged=key["flagged"],
                flag_reason=key["reason"],
            )
            db.add(rk)
            count += 1
    db.commit()
    return count


@router.post("/cases/{case_id}/registry/parse")
def parse_registry(case_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    evidence = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).first()
    if not evidence:
        raise HTTPException(404, "No evidence found")
    count = _seed_registry(db, case_id, evidence.id)
    log_action(db, case_id, "registry_parsed", f"{count} registry keys extracted")
    return {"status": "complete", "keys_extracted": count}


@router.get("/cases/{case_id}/registry/keys", response_model=List[schemas.RegistryKeyOut])
def list_registry_keys(
    case_id: str,
    hive: Optional[str] = None,
    category: Optional[str] = None,
    flagged_only: bool = False,
    db: Session = Depends(get_db)
):
    q = db.query(models.RegistryKey).filter(models.RegistryKey.case_id == case_id)
    if hive:
        q = q.filter(models.RegistryKey.hive == hive)
    if category:
        q = q.filter(models.RegistryKey.category == category)
    if flagged_only:
        q = q.filter(models.RegistryKey.flagged == True)
    return q.order_by(models.RegistryKey.last_modified.desc()).all()


@router.get("/cases/{case_id}/registry/summary")
def registry_summary(case_id: str, db: Session = Depends(get_db)):
    total = db.query(models.RegistryKey).filter(models.RegistryKey.case_id == case_id).count()
    flagged = db.query(models.RegistryKey).filter(
        models.RegistryKey.case_id == case_id, models.RegistryKey.flagged == True
    ).count()
    from sqlalchemy import func
    by_hive = db.query(
        models.RegistryKey.hive, func.count(models.RegistryKey.id)
    ).filter(models.RegistryKey.case_id == case_id).group_by(models.RegistryKey.hive).all()
    return {"total": total, "flagged": flagged, "by_hive": [{"hive": h[0], "count": h[1]} for h in by_hive]}
