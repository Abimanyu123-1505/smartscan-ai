"""
Chain-of-custody logging with hash-chained, tamper-evident entries.

Each entry's hash covers the previous entry's hash plus its own fields,
so the audit log for a case forms a linked chain (per-case, since each
case is an isolated evidence store). Modifying, deleting, or reordering
a past entry breaks every hash after it -- `verify_chain()` walks the
chain and reports exactly where it breaks, so investigators (or a court)
can confirm the log wasn't altered after the fact.
"""
import hashlib
from sqlalchemy.orm import Session
from .. import models

GENESIS_HASH = "0" * 64


def _entry_hash(prev_hash: str, actor: str, action: str, detail: str, timestamp) -> str:
    payload = f"{prev_hash}|{actor}|{action}|{detail}|{timestamp.isoformat()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_action(db: Session, case_id: str, action: str, detail: str = "", actor: str = "analyst"):
    last = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.case_id == case_id)
        .order_by(models.AuditLog.timestamp.desc())
        .first()
    )
    prev_hash = last.entry_hash if last else GENESIS_HASH

    entry = models.AuditLog(case_id=case_id, actor=actor, action=action, detail=detail)
    # timestamp is assigned by the column default on flush; compute the
    # hash against that exact value so it matches on verification.
    db.add(entry)
    db.flush()
    entry.prev_hash = prev_hash
    entry.entry_hash = _entry_hash(prev_hash, actor, action, detail, entry.timestamp)
    db.commit()
    return entry


def verify_chain(db: Session, case_id: str) -> dict:
    """Recomputes every entry's hash in timestamp order and confirms it
    matches both the stored hash and the next entry's prev_hash. Returns
    {"ok": bool, "checked": int, "broken_at": id|None}."""
    entries = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.case_id == case_id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )
    expected_prev = GENESIS_HASH
    for entry in entries:
        recomputed = _entry_hash(expected_prev, entry.actor, entry.action, entry.detail, entry.timestamp)
        if entry.prev_hash != expected_prev or entry.entry_hash != recomputed:
            return {"ok": False, "checked": len(entries), "broken_at": entry.id}
        expected_prev = entry.entry_hash
    return {"ok": True, "checked": len(entries), "broken_at": None}
