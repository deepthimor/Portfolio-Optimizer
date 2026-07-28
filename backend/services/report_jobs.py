from backend.models import ReportJob
from backend.schemas.portfolio import ReportJobCreateRequest, ReportRequest
from backend.services.scenario_report import build_scenario_report


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
    request_json = request.model_dump()

    job = ReportJob(
        portfolio_id=request.portfolio_id,
        status="pending",
        request_json=request_json,
        result_json=None,
        error_message=None,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        report_request = ReportRequest(
            cash=request.cash,
            holdings=request.holdings,
            scenarios=request.scenarios,
        )

        result = build_scenario_report(report_request)

        job.status = "completed"
        job.result_json = result
        job.error_message = None

    except Exception as error:
        job.status = "failed"
        job.result_json = None
        job.error_message = str(error)

    db.commit()
    db.refresh(job)

    return job


def get_report_job(db, job_id: int) -> ReportJob | None:
    return db.query(ReportJob).filter(ReportJob.id == job_id).first()