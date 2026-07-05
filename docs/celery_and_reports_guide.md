# Celery and Automated Reports Guide

## Overview
This module configures Celery to handle asynchronous background tasks, specifically the generation of daily trading reports. The system utilizes RabbitMQ as the message broker and Redis as the result backend.

## Celery Configuration
The Celery application is instantiated in `src/core/celery.py`.
- **Broker**: `amqp://guest:guest@localhost:5672//`
- **Backend**: `redis://localhost:6379/0`
- **Tasks Modules**: Automatically discovers tasks in `src.modules.reports.tasks`.

## Task: `generate_daily_report_task`
This asynchronous task takes a `user_id` and performs the following operations:
1. Queries recent market data.
2. Queries the user's trading journal entries for the day.
3. Compiles a Markdown formatted report using `ReportService.generate_daily_report()`.
4. Saves the report to disk (or theoretically, sends it via email).

## Running the Worker
The celery worker is configured to run automatically using Docker Compose. Ensure the worker is started by reviewing the `docker-compose.yml`.

To run the worker locally without Docker:
```bash
cd backend
celery -A src.core.celery worker --loglevel=info
```

## Creating Additional Tasks
To create more tasks:
1. Define a function in a `tasks.py` file.
2. Decorate it with `@celery_app.task`.
3. Add the module path to the `include` array in `src/core/celery.py`.
