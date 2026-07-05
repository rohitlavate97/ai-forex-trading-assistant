# Feature Guide - Authentication & Role-Based Access Control (RBAC)

This guide documents the business logic, security structure, database design, API schemas, and usage of the Authentication and RBAC systems.

---

## 1. Business Requirement

*   **Goal**: Authenticate users, identify their profiles, and secure endpoints from unauthorized usage.
*   **Role Management**: Restrict system configuration changes, logs, database updates, and admin functions to authorized personnel (`Admin`), while allowing standard functions (AI Chat, Strategy, Journal) to `Trader` users.
*   **Auditing**: Every database write and agent call must be tagged with the active user's UUID for accountability and auditing.

---

## 2. Financial & Domain Context

While Authentication is a standard software layer, the trading system demands specific constraints:
*   **Auditability**: Regulators and risk managers must be able to trace who initiated a trading journal review or adjusted simulated leverage/risk parameters.
*   **Tenant/User Isolation**: Ensure that user papers, journal reviews, and knowledge bases remain completely private to the user. No user can view or alter another trader's dashboard or portfolio.

---

## 3. Architecture

Clean Architecture principles segment the module into layers:

```
FastAPI Router (API Entry)
      │
      ▼
Dependencies (get_current_user / RoleChecker)
      │
      ▼
AuthService (Business Rules & Token Logic)
      │
      ▼
UserRepository (SQLAlchemy Data Layer)
      │
      ▼
MySQL Database (Users Table)
```

---

## 4. Database Design

### Relational Schema (MySQL)
The module maps to the `users` table:

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'trader',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    created_by VARCHAR(36),
    updated_by VARCHAR(36),
    INDEX idx_user_uuid (uuid),
    INDEX idx_user_username (username),
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
);
```

---

## 5. API Design

All endpoints reside under `/api/v1/auth`.

### Endpoints:
1.  **POST `/api/v1/auth/register`**:
    *   *Payload*: `UserCreate` (email, username, password, optional role)
    *   *Response*: `UserResponse` (strip password hash)
2.  **POST `/api/v1/auth/login`**:
    *   *Payload*: URL-encoded Form (`username`, `password`)
    *   *Response*: `Token` (access_token, refresh_token, bearer)
3.  **POST `/api/v1/auth/refresh`**:
    *   *Payload*: Query/Body `refresh_token`
    *   *Response*: `Token`
4.  **GET `/api/v1/auth/me`**:
    *   *Security*: Bearer Token
    *   *Response*: `UserResponse`
5.  **GET `/api/v1/auth/admin-only`**:
    *   *Security*: Bearer Token (must have role `admin`)
    *   *Response*: `{"message": "..."}`

---

## 6. Backend Design

*   **Password Hashing**: Uses `passlib[bcrypt]` to hash passwords on registry, and verify them on login.
*   **Token Standard**: Uses `PyJWT` to generate self-contained, signed JSON Web Tokens. Access tokens default to **30 minutes** validity; refresh tokens default to **7 days**.
*   **Security Context**: Token decoding uses `HS256` hashing signature using the configured `SECRET_KEY`.

---

## 7. Gradio Frontend Design

Gradio UI elements will authenticate requests using a persistent browser state object. When the app initializes:
1. If no tokens exist, the UI renders the Login/Registration views.
2. Upon successful POST to `/api/v1/auth/login`, tokens are saved in Gradio's state variable (`gr.State`).
3. Subsequent REST calls add the bearer token to the request headers: `Authorization: Bearer <access_token>`.

---

## 8. Security & OWASP Defenses

*   **Password Complexity**: Pydantic validates password lengths during registration (min 8 characters).
*   **Username Guardrails**: The username pattern restricts input to letters, numbers, hyphens, and underscores (`^[a-zA-Z0-9_-]+$`) to prevent injection attacks.
*   **Inactive Accounts**: Users with `is_active=False` are rejected during both token validation and password authentication.
*   **Least Privilege**: The `RoleChecker` dependency implements RBAC at the routing level before endpoint controllers compile data.

---

## 9. Testing

The module includes unit and mock-integration tests in [backend/tests/test_auth.py](file:///D:/Projects/Full%20Stack%20apps/ai-forex-trading-assistant/backend/tests/test_auth.py):
*   `test_password_hashing`: Verifies bcrypt salting, encryption, and matching.
*   `test_jwt_generation_and_decoding`: Tests payload parsing, expire verification, and sub validation.
*   `test_auth_service_registration_success`: Mocks repository calls to assert user insertion.
*   `test_auth_service_registration_duplicate_username` & `test_auth_service_registration_duplicate_email`: Asserts error codes (400 Bad Request) on credential collisions.

---

## 10. Performance

*   **Database Query Optimization**: The MySQL fields `uuid`, `username`, and `email` are indexed to execute lookup operations in O(1) time complexity.
*   **Cryptography Overhead**: Hashing passwords using Bcrypt requires significant CPU cycles by design. This acts as a rate limit to prevent brute force login attempts.

---

## 11. Common Mistakes

*   **Hardcoding SECRET_KEY**: Using a default key in code exposes JWT signatures. Resolved by using Pydantic Settings, which loads settings from env variables and errors out if `SECRET_KEY` is missing in production.
*   **Returning Password Hashes**: Returning the password hash in the API response. Prevented by using the Pydantic `UserResponse` DTO, which explicitly excludes `hashed_password`.

---

## 12. Interview Questions

1.  **Why do we use UUIDs instead of auto-incrementing integer IDs in public APIs?**
    *   *Answer*: Auto-incrementing IDs (`1`, `2`, `3`) allow enumeration attacks, letting malicious users scrape profiles or estimate user volumes. UUIDs are random and impossible to guess.
2.  **What is the difference between encryption and hashing?**
    *   *Answer*: Encryption is two-way (decryptable with a key). Hashing is one-way (mathematically irreversible). Passwords must always be hashed.
