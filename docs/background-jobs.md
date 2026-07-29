# Background Jobs

## Queue Choice

For this version, the project uses a simple database-backed job table and a lightweight worker command.

Instead of adding Redis, Celery, or RQ immediately, the API creates a report job record, stores the request payload, and marks the job as `pending`. A separate worker command reads pending jobs, runs deterministic scenario report calculations, saves `result_json`, and updates the job status to `completed` or `failed`.

## Why This Choice

This approach is intentionally simple for the MVP.

Benefits:

- Easy to explain in interviews
- No extra infrastructure required
- Works locally with the existing database setup
- Gives report generation a real lifecycle
- Supports `pending`, `running`, `completed`, and `failed` states before Redis/Celery/RQ are added

Tradeoffs:

- It is not a distributed queue
- It does not process jobs continuously yet
- A developer must run the worker command manually
- It is less scalable than Redis/Celery/RQ
- It is still enough to prove job lifecycle, persistence, status checking, and worker behavior

## Future Upgrade Path

A future version can replace the lightweight worker command with a real queue system.

Possible options:

- Redis + RQ for a simple Python queue
- Redis + Celery for a mature distributed task system
- Cloud-native queues if deployed on managed infrastructure

## Job Lifecycle

Current lifecycle:

```text
POST /api/reports
    -> create job with status=pending
    -> store request_json
    -> return job_id and status

PYTHONPATH=. python scripts/run_worker.py
    -> read pending report job
    -> mark status=running
    -> run deterministic scenario report
    -> save result_json
    -> mark status=completed

If calculation fails:
    -> save error_message
    -> mark status=failed

GET /api/reports/{id}
    -> return current job status, result_json, or error_message
```

## Job States

Supported states:

- `pending`
- `running`
- `completed`
- `failed`

## Worker Command

Run the worker locally:

```bash
PYTHONPATH=. python scripts/run_worker.py
```

The worker processes pending report jobs and logs:

- job_id
- status transitions
- duration
- errors

## Restart Behavior

Report jobs are stored in the database, not only in memory.

That means:

- If the backend restarts, existing jobs remain in the database.
- If the worker stops, pending jobs remain pending.
- If the worker restarts, it can continue processing pending jobs.
- Completed jobs keep their stored `result_json`.
- Failed jobs keep their stored `error_message`.

## Report Job Table

The report job table stores:

- id
- portfolio_id
- status
- request_json
- result_json
- error_message
- created_at
- updated_at