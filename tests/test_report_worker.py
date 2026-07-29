import logging

from sqlalchemy.orm import sessionmaker

from backend.schemas.portfolio import ReportJobCreateRequest
from backend.services.report_jobs import create_report_job, get_report_job
from backend.services.report_worker import process_next_report_job


def make_report_request(scenarios=None):
    return ReportJobCreateRequest(
        cash=1000,
        portfolio_id=None,
        scenarios=scenarios or ["market_down_25"],
        holdings=[
            {
                "ticker": "AAPL",
                "quantity": 10,
                "price": 100,
                "asset_class": "stock",
                "sector": "technology",
            },
            {
                "ticker": "BND",
                "quantity": 10,
                "price": 80,
                "asset_class": "bond",
                "sector": "fixed income",
            },
        ],
    )


def test_worker_processes_report_successfully(db_session):
    job = create_report_job(db_session, make_report_request())

    assert job.status == "pending"

    processed_job = process_next_report_job(db_session)

    assert processed_job.id == job.id
    assert processed_job.status == "completed"
    assert processed_job.result_json["starting_value"] == 2800
    assert processed_job.result_json["results"][0]["scenario_name"] == "market_down_25"
    assert processed_job.error_message is None


def test_worker_marks_failed_job_and_stores_error_message(db_session):
    job = create_report_job(
        db_session,
        make_report_request(["made_up_scenario"]),
    )

    processed_job = process_next_report_job(db_session)

    assert processed_job.id == job.id
    assert processed_job.status == "failed"
    assert processed_job.result_json is None
    assert "unknown scenario name" in processed_job.error_message


def test_worker_logs_job_flow(db_session, caplog):
    caplog.set_level(logging.INFO)

    job = create_report_job(db_session, make_report_request())

    process_next_report_job(db_session)

    log_messages = "\n".join(record.getMessage() for record in caplog.records)

    assert f"job_id={job.id}" in log_messages
    assert "status_transition=pending->running" in log_messages
    assert "status_transition=running->completed" in log_messages
    assert "duration_seconds=" in log_messages


def test_report_result_persists_after_new_database_session(db_session):
    job = create_report_job(db_session, make_report_request())
    job_id = job.id

    process_next_report_job(db_session)

    NewSession = sessionmaker(bind=db_session.bind)
    new_db = NewSession()

    try:
        persisted_job = get_report_job(new_db, job_id)

        assert persisted_job is not None
        assert persisted_job.status == "completed"
        assert persisted_job.result_json["starting_value"] == 2800
    finally:
        new_db.close()


def test_worker_returns_none_when_no_pending_jobs(db_session):
    processed_job = process_next_report_job(db_session)

    assert processed_job is None