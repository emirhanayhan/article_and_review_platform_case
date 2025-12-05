# 🛡️ Identity and Access Management (IAM) Microservice

This microservice is responsible for handling all core user identity, authentication, and authorization processes using JSON Web Tokens (JWTs). It serves as the single source of truth for user accounts and role definitions within the overall system architecture.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.13
* PostgreSQL


### Setup

1.  **Clone the Repository:**
    ```bash
    git clone git
    cd [YOUR_REPO_DIR]
    ```

2.  **Install Dependencies:**
    ```bash
    # Assuming you are using Poetry
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Project can be started with local configuration without settings
    env but for prod and stage config this env's are expected
    ```env
    ENV -- DEFAULT (only on local configuration)
    HOST -- 0.0.0.0
    PORT -- 8000
    POSTGRES_CONNECTION_STRING -- postgresql+asyncpg://0.0.0.0:5432/iam
    WORKER_COUNT -- 1 increase if needed
    REFRESH_TOKEN_TTL -- 432000
    ACCESS_TOKEN_TTL -- 86400
    ```

4. **Start the Service:**
    Run with auto migration and prod config
    ```bash
    python main.py --config=prod --migrate=true
    ```
    Run without migration
    ```bash
    python main.py --config=local
    ```

---

## 🎯 Key Endpoints

The service primarily exposes unauthenticated endpoints for account creation and token generation, and secured endpoints (once authenticated) for user-specific data.

### 1. Health and Documentation

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/healthcheck` | Confirms the API is running and connected to the database. |

### 2. Authentication and Users

| Method | Path | Name | Description                                                   | Requires Auth |
|:-------| :--- | :--- |:--------------------------------------------------------------| :--- |
| `POST` | `/api/v1/users` | `create_user` | Creates a new user account (registration).                    | No |
| `POST` | `/api/v1/tokens` | `create_token` | Generates a new **Access Token (JWT)** upon successful login. | No |
| `ME`   | `/api/v1/me` | `get_me` | Verifies user token and return user data.                     | **Yes** |

### 3. Roles and Authorization

| Method | Path | Name | Description |
| :--- | :--- | :--- | :--- | :-- |
| `POST` | `/api/v1/roles` | `create_role` | Creates a new role definition (e.g., 'admin', 'editor'). | **Yes (Admin)** |

---

## 🔐 Authentication Flow

1.  A client makes a `POST` request to `/api/v1/tokens` with valid user credentials (email/password).
2.  The IAM service authenticates the user, looks up their **Role and Permissions**, and signs a JWT (Access Token) using the **RS256** algorithm.
3.  The client receives the JWT.
4.  For all subsequent requests to protected endpoints (e.g., `/api/v1/me`), the client includes the JWT in the `Authorization: Bearer <token>` header.
5.  The IAM service (or other microservices) verifies the token's signature using the globally shared **Public Key**.

---

## 💡 Architecture Notes

* **Algorithm:** Uses **RS256** for JWT signing, allowing other microservices to verify tokens without contacting the IAM service, using only the public key.
* **Authorization Model:** Utilizes **Role-Based Access Control (RBAC)**, with permissions being determined by the user's assigned role.
