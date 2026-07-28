from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.portfolio import (
    ReportJobCreateRequest,
    ReportJobCreateResponse,
    ReportJobStatusResponse,
)
from backend.services.report_jobs import create_report_job, get_report_job, serialize_report_job

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.post("", response_model=ReportJobCreateResponse)
def create_report(request: ReportJobCreateRequest, db: Session = Depends(get_db)):
    job = create_report_job(db, request)

    return {
        "job_id": job.id,
        "status": job.status,
    }


@router.get("/{job_id}", response_model=ReportJobStatusResponse)
def get_report_status(job_id: int, db: Session = Depends(get_db)):
    job = get_report_job(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="report job not found")

    return serialize_report_job(job)