# Trading Journal Management Guide

## Overview
The Trading Journal module allows traders to keep comprehensive records of their trades, including entry and exit prices, profit and loss, notes, and specific tags (e.g., `#NFP`, `#TrendFollowing`).

## Architecture
- **Router** (`src/modules/journal/router.py`): Exposes standard CRUD endpoints.
- **Service** (`src/modules/journal/service.py`): Houses the core logic for database transactions and business rules.
- **Models** (`src/modules/journal/models.py`): SQLAlchemy schemas with relationships back to the `User` table.
- **Schemas** (`src/modules/journal/schemas.py`): Pydantic schemas validating API requests and responses.

## API Reference

### 1. Create a Journal Entry
**Endpoint:** `POST /api/v1/journal/`
**Requires Authentication:** Yes
**Payload:**
```json
{
  "currency_pair": "EUR/USD",
  "direction": "LONG",
  "entry_price": 1.0950,
  "exit_price": 1.1000,
  "profit_loss": 50.0,
  "notes": "Entered on strong momentum after PMI data release.",
  "tags": ["#PMI", "#trend"]
}
```

### 2. Retrieve All Entries
**Endpoint:** `GET /api/v1/journal/`
**Requires Authentication:** Yes
**Description:** Fetches all journal entries for the currently authenticated user, ordered by creation date descending.

### 3. Retrieve a Single Entry
**Endpoint:** `GET /api/v1/journal/{entry_id}`
**Requires Authentication:** Yes
**Description:** Fetches a specific journal entry. Returns 404 if it does not exist or doesn't belong to the user.

### 4. Update an Entry
**Endpoint:** `PATCH /api/v1/journal/{entry_id}`
**Requires Authentication:** Yes
**Description:** Partially updates an existing journal entry. Useful for logging the exit price and profit/loss after a trade completes.

### 5. Delete an Entry
**Endpoint:** `DELETE /api/v1/journal/{entry_id}`
**Requires Authentication:** Yes
**Description:** Deletes a specific journal entry permanently. Returns 204 No Content on success.

## Database
The module uses the `journal_entries` table. Ensure you run the necessary Alembic migrations to construct this table:
```bash
python -m alembic upgrade head
```
