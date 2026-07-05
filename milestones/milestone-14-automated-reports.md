# Milestone 14: Automated Report Generation (Celery Setup)

**Status**: Completed
**Tag**: `v0.14-automated-reports`

## Objective
Set up Celery with RabbitMQ and Redis to execute asynchronous background tasks, specifically to generate automated daily trading reports in Markdown format.

## Implementation Details
1. **Celery Configuration**:
   - Initialized the Celery application in `backend/src/core/celery.py`.
   - Configured RabbitMQ as the message broker and Redis as the result backend using application settings.
   - Updated `backend/src/core/config.py` to expose necessary message broker variables.
2. **Report Generation Service**:
   - Created `backend/src/modules/reports/service.py`.
   - Implemented `ReportService.generate_daily_report()` to aggregate market data and journal entries into a clean Markdown string.
3. **Celery Task**:
   - Created `backend/src/modules/reports/tasks.py`.
   - Registered `generate_daily_report_task` which utilizes the `ReportService` and persists the output securely.
4. **Docker Integration**:
   - Uncommented and configured the `worker` service in `docker-compose.yml` to automatically spin up a Celery worker alongside the web backend.
5. **Testing**:
   - Authored `backend/tests/test_celery_tasks.py`.
   - Mocked file system I/O using `unittest.mock.patch` to verify task behavior without modifying disk contents.

## Deliverables
- Functioning Celery configuration for background processing.
- Automated daily report generation logic.
- Updated infrastructure config (docker-compose).
- Developer guide `docs/celery_and_reports_guide.md`.
