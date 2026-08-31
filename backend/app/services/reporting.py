"""
Report Generator (Phase 1 deliverable): exportable PDF/HTML case reports
with a summary, hash list, and timeline -- citing back to evidence IDs
for traceability, per NIST SP 800-86 style reporting.
"""
import io
import datetime as dt
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from sqlalchemy.orm import Session
from .. import models


def build_case_pdf(db: Session, case: models.Case) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=LETTER, title=f"DFIOP Case Report - {case.name}")
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#1a1f29"))
    story = []

    story.append(Paragraph(f"DFIOP Case Report: {case.name}", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Case ID: {case.id}", styles["Normal"]))
    story.append(Paragraph(f"Investigator: {case.investigator or 'n/a'}", styles["Normal"]))
    story.append(Paragraph(f"Status: {case.status}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {dt.datetime.utcnow().isoformat()}Z", styles["Normal"]))
    story.append(Paragraph(f"Description: {case.description or 'n/a'}", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Evidence & Hashes", styles["Heading2"]))
    evidence_rows = [["Filename", "Type", "SHA-256", "Acquired"]]
    for ev in case.evidence_items:
        evidence_rows.append([
            ev.original_filename, ev.evidence_type,
            ev.sha256[:16] + "…", ev.acquired_at.strftime("%Y-%m-%d %H:%M UTC"),
        ])
    ev_table = Table(evidence_rows, hAlign="LEFT", colWidths=[140, 90, 140, 110])
    ev_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1f29")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f6")]),
    ]))
    story.append(ev_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Timeline (most recent 100 events)", styles["Heading2"]))
    events = (
        db.query(models.TimelineEvent)
        .filter(models.TimelineEvent.case_id == case.id)
        .order_by(models.TimelineEvent.event_ts.desc())
        .limit(100)
        .all()
    )
    tl_rows = [["Timestamp", "Type", "Summary"]]
    for e in events:
        tl_rows.append([e.event_ts.strftime("%Y-%m-%d %H:%M:%S"), e.event_type, e.summary[:70]])
    tl_table = Table(tl_rows, hAlign="LEFT", colWidths=[110, 60, 310])
    tl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1f29")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f6")]),
    ]))
    story.append(tl_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("Chain of Custody", styles["Heading2"]))
    logs = (
        db.query(models.AuditLog)
        .filter(models.AuditLog.case_id == case.id)
        .order_by(models.AuditLog.timestamp.asc())
        .all()
    )
    log_rows = [["Timestamp", "Actor", "Action", "Detail"]]
    for l in logs:
        log_rows.append([l.timestamp.strftime("%Y-%m-%d %H:%M:%S"), l.actor, l.action, l.detail[:50]])
    log_table = Table(log_rows, hAlign="LEFT", colWidths=[100, 60, 90, 230])
    log_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1f29")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f6")]),
    ]))
    story.append(log_table)

    doc.build(story)
    return buf.getvalue()
