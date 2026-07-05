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
