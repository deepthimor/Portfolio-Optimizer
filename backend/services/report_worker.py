import logging
import time

from backend.models import ReportJob
from backend.schemas.portfolio import ReportRequest
from backend.services.scenario_report import build_scenario_report
from backend.services.logging_utils import get_request_id

logger = logging.getLogger(__name__)


def build_user_friendly_error(error: Exception) -> str:
    raw_error = str(error)

    if "unknown scenario name" in raw_error:
        return (
            "Report failed because the request included an unsupported scenario. "
            f"Details: {raw_error}"
        )

    if "portfolio value must be greater than zero" in raw_error:
        return (
            "Report failed because the portfolio value must be greater than zero. "
            f"Details: {raw_error}"
        )

    return (
        "Report failed during deterministic scenario processing. "
        f"Details: {raw_error}"
    )


def get_next_pending_report_job(db) -> ReportJob | None:
    return (
        db.query(ReportJob)
        .filter(ReportJob.status == "pending")
        .order_by(ReportJob.created_at.asc(), ReportJob.id.asc())
        .first()
    )


def mark_job_running(db, job: ReportJob) -> ReportJob:
    previous_status = job.status
    job.status = "running"

    db.commit()
    db.refresh(job)

    logger.info(
        "request_id=%s job_id=%s status_transition=%s->running",
        get_request_id(),
        job.id,
        previous_status,
    )

    return job


def mark_job_completed(db, job: ReportJob, result: dict, duration_seconds: float) -> ReportJob:
    previous_status = job.status
    job.status = "completed"
    job.result_json = result
    job.error_message = None

    db.commit()
    db.refresh(job)

    logger.info(
        "request_id=%s job_id=%s status_transition=%s->completed duration_seconds=%.4f",
        get_request_id(),
        job.id,
        previous_status,
        duration_seconds,
    )

    return job


def mark_job_failed(db, job: ReportJob, error: Exception, duration_seconds: float) -> ReportJob:
    previous_status = job.status
    job.status = "failed"
    job.result_json = None
    job.error_message = build_user_friendly_error(error)

    db.commit()
    db.refresh(job)

    logger.exception(
        "request_id=%s job_id=%s status_transition=%s->failed duration_seconds=%.4f error_type=%s",
        get_request_id(),
        job.id,
        previous_status,
        duration_seconds,
        type(error).__name__,
    )

    return job


def build_report_request_from_job(job: ReportJob) -> ReportRequest:
    request_json = job.request_json or {}

    return ReportRequest(
        cash=request_json.get("cash", 0),
        holdings=request_json.get("holdings", []),
        scenarios=request_json.get("scenarios"),
    )


def process_report_job(db, job: ReportJob) -> ReportJob:
    started_at = time.perf_counter()

    logger.info(
        "request_id=%s job_id=%s worker_started status=%s",
        get_request_id(),
        job.id,
        job.status,
    )

    mark_job_running(db, job)

    try:
        report_request = build_report_request_from_job(job)
        result = build_scenario_report(report_request)

        duration_seconds = time.perf_counter() - started_at

        return mark_job_completed(db, job, result, duration_seconds)

    except Exception as error:
        duration_seconds = time.perf_counter() - started_at

        return mark_job_failed(db, job, error, duration_seconds)


def process_next_report_job(db) -> ReportJob | None:
    job = get_next_pending_report_job(db)

    if not job:
        logger.info(
            "request_id=%s worker_checked_queue pending_jobs=0",
            get_request_id(),
        )
        return None

    return process_report_job(db, job)


def process_pending_report_jobs(db, limit: int = 10) -> int:
    processed_count = 0

    for _ in range(limit):
        job = process_next_report_job(db)

        if not job:
            break

        processed_count += 1

    logger.info(
        "request_id=%s worker_finished processed_count=%s",
        get_request_id(),
        processed_count,
    )

    return processed_count