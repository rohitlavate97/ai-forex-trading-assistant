# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created repository folder structure for backend (FastAPI) and frontend (Gradio).
- Configured project settings in `pyproject.toml` including configurations for Ruff linter/formatter, MyPy type checks, and Pytest.
- Added `.pre-commit-config.yaml` for enforcing standard checks, formatting, and linting.
- Drafted `.env.example` with comprehensive service credentials and provider configurations.
- Created `requirements.txt` files for both frontend and backend packages.
- Added basic placeholder entrypoints `backend/src/main.py` and `frontend/app.py` for sanity testing.
- Initialized Git branch `milestone-01-project-setup` for the project setup tasks.
- Configured GitHub Actions CI pipeline (`ci.yml`) to automatically validate code styling, linting, typing, and test compliance.
- Set up testing directories and placeholder test modules for both backend and frontend.
- Created `Dockerfile` configuration for the FastAPI backend and Gradio frontend services.
- Added `docker-compose.yml` to orchestrate MySQL 8.4, Redis 7, RabbitMQ 3, Qdrant vector DB, and the application services.
- Created `docs/developer_setup_guide.md` covering prerequisites, environment configurations, Docker Compose tasks, and troubleshooting steps.
- Created `docs/adr/0001-agent-framework-selection.md` outlining the architectural rationale for choosing Pydantic AI for specialist agents and LangGraph for the coordinator.

## [0.2.0] - Unreleased

### Added
- Created `backend/src/core/config.py` using `pydantic-settings` to securely validate environment variables.
- Created `backend/src/core/database.py` configuring SQLAlchemy async engine, session makers, base models, and db dependencies.
- Added `User` database models with UUID representation, encryption passwords, roles enum, and audit columns in `backend/src/modules/auth/models.py`.
- Created Pydantic DTO validation schemas for User registration, updates, login, and token generation in `backend/src/modules/auth/schemas.py`.
- Developed security utilities in `backend/src/modules/auth/security.py` covering password hashing (bcrypt) and JWT creation/verification using PyJWT.
- Implemented `UserRepository` for User persistence operations, `AuthService` handling registration and authentication flow, and OAuth2 security dependencies with `RoleChecker` for Role-Based Access Control (RBAC).
- Created endpoints for user registration, token login, refresh, user profiles, and RBAC admin-only validations under `/api/v1/auth`, and integrated the router into the main FastAPI application.
- Added comprehensive authentication test suite in `backend/tests/test_auth.py` covering password hashing, JWT operations, and service registration validations.
- Documented authentication architecture, relational schemas, REST endpoints, and security implementations in `docs/auth_guide.md`.

## [0.3.0] - Unreleased

### Added
- Created `milestones` folder containing markdown summary records for Milestone 1 and Milestone 2.
- Loosened package dependencies versions in `backend/requirements.txt` to enable smooth python package resolutions.
- Initialized Alembic database migrations framework in `backend/alembic` and configured `backend/alembic/env.py` to support asynchronous migrations.
- Created the initial database migration script `0001_create_users_table.py` for mapping users schema to MySQL.
- Developed an idempotent database seeding script `backend/src/scripts/seed_db.py` to populate baseline admin and trader accounts.
- Documented schema migration commands, connection pool details, and setup parameters in `docs/database_guide.md`.

## [0.4.0] - Unreleased

### Added
- Created global async Redis connection manager in `backend/src/core/redis.py` for caching live price rates and rate limit details.
- Added strict incoming price tick schemas and extreme price deviation validation rules in `backend/src/modules/market_data/validation.py`.
- Developed mock WebSocket feed generator server in `backend/src/modules/market_data/mock_provider.py` to broadcast simulated forex ticks for local testing.
- Created `MarketDataIngestionService` in `backend/src/modules/market_data/ingestion.py` featuring WebSocket connectivity, exponential backoff reconnects, and Redis cache streaming.
- Implemented `MarketDataService` and FastAPI router endpoints under `/api/v1/market-data` for live currency queries, tick histories, and feed metrics.
- Integrated database connection verification and Redis ping checks into the `/health` endpoint and configured FastAPI lifespan events to manage background tasks.
- Added market data validation and feed resilience tests in `backend/tests/test_market_data.py` to ensure schema constraints and deviation checks are fully operational.
- Created Market Data Ingestion and Caching feature guide in `docs/market_data_guide.md` detailing pip concepts, validation thresholds, and API specs.

## [0.5.0] - Unreleased

### Added
- Created premium Dark-Mode Bloomberg/TradingView style CSS stylesheet in `frontend/src/theme.css` to govern Gradio layouts.
- Developed `ForexAPIClient` in `frontend/src/api_client.py` using `httpx` to handle async communications with backend market-data endpoints.
- Updated `frontend/app.py` with custom theme integration, card templates, and real-time dashboard layout featuring live quotes, watchlist metrics, and market mover tables.
- Wired a 2-second `gr.Timer` polling loop to dynamically fetch rates and refresh the UI layout.
- Added API client unit tests in `frontend/tests/test_dashboard.py` verifying response parsing and HTTP error handling.
- Created Gradio Dashboard layout and timer polling feature guide in `docs/dashboard_guide.md` covering UI styles, layouts, and API client specs.

## [0.6.0] - Unreleased

### Added
- Implemented mathematical algorithms for standard technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Fibonacci Retracement, Ichimoku Cloud) in `backend/src/modules/agents/tech_analysis/calculators.py`.
- Developed database-querying agent tools `tool_get_indicators_summary` and `tool_get_advanced_indicators` in `backend/src/modules/agents/tech_analysis/tools.py`.
- Programmed `tech_analysis_agent` using Pydantic AI in `backend/src/modules/agents/tech_analysis/agent.py` and saved the versioned specialist system guidelines in `backend/src/modules/agents/tech_analysis/prompts.py`.
- Added technical analysis tests in `backend/tests/test_tech_analysis.py` covering indicators calculators and mocked agent runs.
- Created Technical Analysis Agent feature guide in `docs/tech_analysis_agent_guide.md` detailing prompt parameters, calculator codes, and tool scopes.

## [0.7.0] - Unreleased

### Added
- Created `EconomicEvent` database model and Alembic schema migration script `d002_create_economic_events_table.py` inside `backend/src/modules/economic_calendar/models.py`.
