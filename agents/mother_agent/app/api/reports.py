from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.report_service import generate_weekly_pdf_report

router = APIRouter(prefix="/api/v1/reports", tags=["Weekly PDF Reports"])


@router.get("/weekly-pdf")
def get_weekly_report_pdf(db: Session = Depends(get_db)):
    """Generates and streams the weekly inventory and forecast report as a PDF."""
    pdf_bytes = generate_weekly_pdf_report(db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=weekly_grocery_report.pdf"}
    )
