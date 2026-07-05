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
