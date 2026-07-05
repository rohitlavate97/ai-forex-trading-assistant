# Local Development Setup Guide

This guide describes how to set up the local environment to run, test, and develop the AI Forex Trading Assistant.

---

## 1. Prerequisites

Ensure you have the following installed on your host machine:

| Dependency | Minimum Version | Verified Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Python** | `3.13` | `3.14.3` | Application Runtime |
| **Docker** | `20.10+` | `28.4.0` | Local Service Orchestration |
| **Docker Compose** | `v2.0+` | `v2.39.4` | Container Orchestration tool |
| **Git** | `2.30+` | `2.40+` | Version Control |

---

## 2. Environment Variables Configuration

The application relies on environment variables for database configurations, keys, and security parameters.

1. Copy the example environment file to create your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the required keys.
   > [!IMPORTANT]
   > Do **NOT** commit the `.env` file to version control. It is already added to `.gitignore`.

### Key Parameters:
*   **OPENAI_API_KEY**: Required for agent operations.
*   **MARKET_DATA_API_KEY**: Needed for live tick rate ingestion.
*   **SECRET_KEY**: Generated locally for JWT token verification.

---

## 3. Running the Stack

You can run the application in two ways: completely dockerized, or in hybrid mode (databases in Docker, python services run natively).

### Option A: Fully Containerized (Recommended for testing)

To boot up MySQL, Redis, RabbitMQ, Qdrant, the FastAPI Backend, and the Gradio Frontend:

```bash
docker-compose up --build -d
```

#### Access Ports:
*   **FastAPI Backend API**: [http://localhost:8000](http://localhost:8000)
*   **FastAPI Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Gradio UI**: [http://localhost:7860](http://localhost:7860)
*   **RabbitMQ Management Console**: [http://localhost:15672](http://localhost:15672) (User: `guest`, Pass: `guest`)
*   **Qdrant REST Dashboard**: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

To view logs:
```bash
docker-compose logs -f
```

To shut down the services:
```bash
docker-compose down
```

---

### Option B: Hybrid Mode (Recommended for active code development)

In this mode, databases run inside containers, while FastAPI and Gradio run natively on your machine for quick compilation and debugging.

#### Step 1: Start Databases only
```bash
docker-compose up -d mysql redis rabbitmq qdrant
```

#### Step 2: Initialize Local Python Virtual Environment
```bash
# Create environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt -r frontend/requirements.txt
```

#### Step 3: Run FastAPI backend
With the virtual environment active:
```bash
fastapi dev backend/src/main.py
```
This runs the server on [http://localhost:8000](http://localhost:8000) with hot-reloading active.

#### Step 4: Run Gradio frontend
In a new terminal window with the virtual environment active:
```bash
python frontend/app.py
```
This serves the frontend UI on [http://localhost:7860](http://localhost:7860).

---

## 4. Alembic Migrations & Database Seeding

Once the database container is online:

1. Run migrations to initialize the schema:
   ```bash
   cd backend
   alembic upgrade head
   ```
2. (Optional) Load sample data for trading pairs, indicators, and calendar events:
   ```bash
   python src/scripts/seed_db.py
   ```

*(Note: Alembic config and seed scripts will be implemented in Milestone 3).*

---

## 5. Running the Test Suite

We use `pytest` for all unit, integration, and API endpoint tests.

### Running Backend Tests
Ensure you are in the virtualenv:
```bash
pytest backend/tests
```

### Running Frontend Tests
```bash
pytest frontend/tests
```

---

## 6. Pre-commit Hooks

We use pre-commit to check code formatting (`ruff-format`), syntax rules (`ruff`), and static typing (`mypy`) prior to git commits.

1. Install pre-commit globally or inside virtualenv:
   ```bash
   pip install pre-commit
   ```
2. Setup git hooks:
   ```bash
   pre-commit install
   ```
3. (Optional) Run checks against all files manually:
   ```bash
   pre-commit run --all-files
   ```

---

## 7. Troubleshooting

### Issue: Port 3306 or 6379 Already in Use
*   **Cause**: You have local MySQL/MariaDB or Redis servers running natively on your computer.
*   **Solution**: Stop local services via Services panel (Windows) or brew services (Mac), or change host mapping ports in your `.env` and `docker-compose.yml` (e.g., `"3307:3306"`).

### Issue: Cannot connect to MySQL on Docker Startup
*   **Cause**: MySQL takes longer to boot up, and backend starts running too quickly.
*   **Solution**: The `docker-compose.yml` health checks handle this automatically. If running hybrid, wait 10 seconds after starting docker before launching `fastapi dev`.

### Issue: OpenAI/Market Data API returns connection errors
*   **Cause**: Invalid keys in your `.env` or network firewall blocking requests.
*   **Solution**: Ensure your keys are correctly populated in `.env` without surrounding quotes (unless containing special spaces), and check internet connectivity.
