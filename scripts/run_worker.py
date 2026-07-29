import logging

from backend.database import SessionLocal
from backend.services.report_worker import process_pending_report_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def main():
    db = SessionLocal()

    try:
        processed_count = process_pending_report_jobs(db)
        print(f"Processed {processed_count} report job(s).")
    finally:
        db.close()


if __name__ == "__main__":
    main()