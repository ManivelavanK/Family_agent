import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.models.weekly_report import WeeklyReport
from app.schemas.response import APIResponse
from app.schemas.weekly_report import WeeklyReportResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/report", tags=["Weekly Reports"])


@router.get("/latest", response_model=APIResponse)
def read_latest_weekly_report(db: Session = Depends(get_db)):
    """
    Retrieves the latest generated weekly health report summary.
    """
    logger.info("Request received: Get latest weekly report")
    report = db.query(WeeklyReport).order_by(WeeklyReport.date.desc()).first()
    if not report:
        logger.info("No weekly reports found in database")
        return APIResponse(
            success=False,
            message="No weekly reports compiled yet."
        )

    data = {
        "id": report.id,
        "date": str(report.date),
        "report_summary": json.loads(report.report_json),
        "pdf_download_url": f"/api/v1/report/{report.id}/pdf",
        "created_at": report.created_at.isoformat()
    }
    return APIResponse(
        success=True,
        message="Latest weekly report retrieved successfully",
        data=data
    )


@router.get("/history", response_model=APIResponse)
def read_weekly_report_history(limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieves history of all compiled weekly health reports.
    """
    logger.info("Request received: Get weekly report history")
    reports = db.query(WeeklyReport).order_by(WeeklyReport.date.desc()).limit(limit).all()
    data = []
    for r in reports:
        data.append({
            "id": r.id,
            "date": str(r.date),
            "report_summary": json.loads(r.report_json),
            "pdf_download_url": f"/api/v1/report/{r.id}/pdf",
            "created_at": r.created_at.isoformat()
        })
    return APIResponse(
        success=True,
        message="Weekly report history retrieved successfully",
        data=data
    )


@router.get("/{report_id}", response_model=APIResponse)
def read_weekly_report(report_id: int, db: Session = Depends(get_db)):
    """
    Retrieves metadata and summary details of a specific weekly report by ID.
    """
    logger.info("Request received: Get weekly report ID %d", report_id)
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        logger.warning("Weekly report read failed: ID %d not found", report_id)
        return APIResponse(
            success=False,
            message="Weekly report not found"
        )
    
    data = {
        "id": report.id,
        "date": str(report.date),
        "report_summary": json.loads(report.report_json),
        "pdf_download_url": f"/api/v1/report/{report.id}/pdf",
        "created_at": report.created_at.isoformat()
    }
    return APIResponse(
        success=True,
        message="Weekly report retrieved successfully",
        data=data
    )


@router.get("/{report_id}/pdf")
def download_weekly_report_pdf(report_id: int, db: Session = Depends(get_db)):
    """
    Streams the compiled PDF health summary file to the client for viewing or download.
    """
    logger.info("Request received: Download PDF for weekly report ID %d", report_id)
    report = db.query(WeeklyReport).filter(WeeklyReport.id == report_id).first()
    if not report:
        logger.warning("PDF download failed: Report ID %d not found", report_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    if not os.path.exists(report.pdf_path):
        logger.error("PDF file not found on disk at path: %s", report.pdf_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF report file not found on server storage"
        )

    filename = os.path.basename(report.pdf_path)
    return FileResponse(
        path=report.pdf_path,
        media_type="application/pdf",
        filename=filename
    )
