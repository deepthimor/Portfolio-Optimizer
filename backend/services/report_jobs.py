from backend.models import ReportJob
from backend.schemas.portfolio import ReportJobCreateRequest


def serialize_report_job(job: ReportJob) -> dict:
    return {
        "job_id": job.id,
        "portfolio_id": job.portfolio_id,
        "status": job.status,
        "request_json": job.request_json,
        "result_json": job.result_json,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
    }


def create_report_job(db, request: ReportJobCreateRequest) -> ReportJob:
    job = ReportJob(
        portfolio_id=request.portfolio_id,
        status="pending",
        request_json=request.model_dump(),
        result_json=None,
        error_message=None,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def get_report_job(db, job_id: int) -> ReportJob | None:
    return db.query(ReportJob).filter(ReportJob.id == job_id).first()