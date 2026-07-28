# Background Jobs

## Queue Choice

For this version, the project uses a simple database-backed job table with synchronous processing.

Instead of adding Redis, Celery, or RQ immediately, the API creates a report job record, stores the request payload, marks the job as `pending`, runs the deterministic scenario report calculation, and then updates the job to `completed` or `failed`.

## Why This Choice

This approach is intentionally simple for the MVP.

Benefits:

- Easy to explain in interviews
- No extra infrastructure required
- Works locally with the existing database setup
- Gives report generation a real lifecycle
- Supports `pending`, `completed`, and `failed` states before a separate worker is added

Tradeoffs:

- The report still runs during the request
- Long-running jobs could block the API request
- It does not support distributed workers yet
- It is not as scalable as Redis/Celery/RQ

## Future Upgrade Path

A future version can replace the synchronous processing step with a real worker system.

Possible options:

- Redis + RQ for a simple Python queue
- Redis + Celery for a more mature distributed task system
- Cloud-native queues if deployed on managed infrastructure

## Job Lifecycle

Current lifecycle:

```text
POST /api/reports
    -> create job with status=pending
    -> run deterministic scenario report
    -> update job to completed or failed
    -> return job_id and status

GET /api/reports/{id}
    -> return current job status and stored result or error
```

## Job States

Supported states:

- `pending`
- `completed`
- `failed`

Future states may include:

- `running`
- `cancelled`
- `retrying`

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