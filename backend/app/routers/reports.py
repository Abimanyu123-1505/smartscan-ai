from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..services.reporting import build_case_pdf
from ..services.audit import log_action

router = APIRouter(prefix="/api/cases", tags=["reports"])


@router.get("/{case_id}/report.pdf")
def get_case_report(case_id: str, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    pdf_bytes = build_case_pdf(db, case)
    log_action(db, case_id, "report_exported", "PDF case report generated", actor="system")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="dfiop_case_{case_id}.pdf"'},
    )
