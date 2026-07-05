# Milestone 1: Project Setup and Orchestration Tooling

Completed on: 2026-07-05
Tag: `v0.1-project-setup`
Branch: `milestone-01-project-setup`

---

## 1. Summary of Achievements

Established the core repository layout and environment definitions for the FastAPI backend and Gradio frontend, ensuring a consistent local development experience across Docker container stacks.

## 2. Added Artifacts & Configurations

*   **Folder Layout**: Decoupled the project into `backend` (FastAPI) and `frontend` (Gradio) modules.
*   **Dependency Management**: Created requirements specifications for both directories (`backend/requirements.txt` and `frontend/requirements.txt`).
*   **Static Analysis & Tooling**: Configured Ruff (linter/formatter) and MyPy (static typing) settings inside `pyproject.toml`.
*   **Git Pre-commit Hooks**: Configured `.pre-commit-config.yaml` to ensure no syntax/formatting errors can be committed.
*   **Environment Templates**: Defined `.env.example` mapping out JWT credentials, database settings, redis caches, broker hosts, and LLM APIs.
*   **Local Setup Guidelines**: Created `docs/developer_setup_guide.md` specifying onboarding steps and running modes (Fully containerized vs Hybrid).
*   **Architectural Log**: Wrote `docs/adr/0001-agent-framework-selection.md` establishing Pydantic AI for specialists and LangGraph for the coordinator agent.
*   **CI Pipeline**: Configured GitHub Actions (`ci.yml`) to automatically execute linters, type checkers, and tests on push.
*   **Orchestration Skeleton**: Created `docker-compose.yml` to launch MySQL 8.4 LTS, Redis 7, RabbitMQ 3, and Qdrant containers with persistent volume mapping and health checks.
