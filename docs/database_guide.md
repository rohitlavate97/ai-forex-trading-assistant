# Feature Guide - Database Foundation (MySQL 8.4 LTS + Alembic)

This guide documents the database architecture, connection pool configurations, schema migration workflows, seeding setups, and best practices.

---

## 1. Business Requirement

*   **Goal**: Establish a transactional, audit-compliant database foundation to store user profiles, portfolio watchlists, economic calendar events, paper trading journal entries, and security audit logs.
*   **Alembic Migrations**: Ensure all schema updates are version-tracked and deployable across staging/production via migration scripts.
*   **Idempotent Seeding**: Provide data seed tools that populate baseline roles and permissions safely without causing duplicate keys or wiping active data.

---

## 2. Architecture & Design

```
    FastAPI Core
         │
         ▼
[core/database.py] (Async Connection Pool & SQLAlchemy Sessionmaker)
         │
   ┌─────┴────────────────────────────────┐
   ▼                                     ▼
Repositories / Services               Alembic env.py
   │                                     │
   └─────────────┬───────────────────────┘
                 │ (aiomysql async connection)
                 ▼
          MySQL Database
```

*   **SQLAlchemy 2.x (Async)**: Configured with `aiomysql` to prevent DB blocking operations from freezing the FastAPI request-response event loops.
*   **Connection Pooling**: Limit connection volumes to 10 connections base and up to 20 overflow to optimize resource utilization.
*   **Metadata Integration**: The `env.py` dynamically imports `Base` metadata and registers models (like `User`) so Alembic can compare model codes against SQL schemas.

---

## 3. Relational Schema Design

The foundational database contains:
1.  **Alembic Version Tracker**: Managed by Alembic to keep record of the active migration ID (`alembic_version`).
2.  **`users` Table**: Declared with indices for quick credential scanning (refer to [docs/auth_guide.md](file:///D:/Projects/Full%20Stack%20apps/ai-forex-trading-assistant/docs/auth_guide.md)).

---

## 4. Migration Workflows

Alembic operations must be executed from the **project root** containing `alembic.ini`. Ensure your virtual environment is active.

### Generating Migrations
When you add or edit a SQLAlchemy model class:
```bash
# Generate a new migration script automatically
.venv\Scripts\python -m alembic revision --autogenerate -m "describe changes here"
```

### Applying Migrations
To bring your database schema up to date with the latest revisions:
```bash
.venv\Scripts\python -m alembic upgrade head
```

### Reverting Migrations
To undo the last migration step:
```bash
.venv\Scripts\python -m alembic downgrade -1
```

---

## 5. Seeding Strategy

The seeding script `backend/src/scripts/seed_db.py` can be executed locally to seed default administrative and trader accounts.

```bash
.venv\Scripts\python backend/src/scripts/seed_db.py
```

### Seed Credentials:
1.  **Administrator**:
    *   *Username*: `admin`
    *   *Email*: `admin@forex.com`
    *   *Password*: `AdminPassword123`
2.  **Trader**:
    *   *Username*: `trader`
    *   *Email*: `trader@forex.com`
    *   *Password*: `TraderPassword123`

---

## 6. Security & Performance

*   **Pre-ping Connections**: The async engine uses `pool_pre_ping=True` to run a light check before fetching connection objects. This detects database drops/disconnects and recycles connections gracefully.
*   **NullPool in Migrations**: During migrations (`env.py`), we use `poolclass=pool.NullPool` to close connections immediately after execution, preventing migrations from locking the database pool.
*   **Environment Loading**: Alembic loads database credentials dynamically from `.env` via our global settings class. No secrets are hardcoded in `alembic.ini`.

---

## 7. Common Mistakes

*   **Autogenerate Missing Imports**: Running `--autogenerate` and finding that it outputs empty migrations.
    *   *Cause*: The newly created model was not imported in `backend/alembic/env.py`.
    *   *Solution*: Make sure to import the model module (e.g. `from src.modules.auth.models import User`) inside `env.py` to register its classes in `Base.metadata`.
*   **Running alembic init in Subfolders**: Running it in the backend folder and creating a separate config.
    *   *Solution*: Run it from the root directory but point `script_location` to `backend/alembic` to keep configuration files at the root level.

---

## 8. Interview Questions

1.  **Why do we use async database sessions in FastAPI instead of standard sync sessions?**
    *   *Answer*: Standard database calls (e.g., waiting for a complex query on 1,000,000 rows) block the executing thread. Under high concurrent traffic, FastAPI's event loop will stall. Async sessions use event-loop callbacks, releasing the thread to process other HTTP requests while waiting for MySQL to return the dataset.
2.  **What is the purpose of Alembic's `--autogenerate` command, and what are its limitations?**
    *   *Answer*: Autogenerate scans SQLAlchemy model definitions and compares them to the active database table structures, generating migration drafts. It is highly convenient but has limitations: it cannot detect table/column renames (it renders them as drops and adds), and it may miss custom database constraints or indexes unless explicitly configured. Autogenerated files must always be manually inspected.
