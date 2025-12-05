# 📝 Article Management Microservice

The article management microservice
---

## 🚀 Getting Started

### Prerequisites

* Python 3.13
* MongoDB 4.4
* Redis 7.10

### Setup

1.**Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Variables:**
    Project can be started with local configuration without settings. The following environment variables are expected for production/staging:

    ```env
    ENV -- DEFAULT (only on local configuration)
    HOST -- 0.0.0.0
    PORT -- 8000
    # Connection string for the Article database
    MONGO_CONNECTION_STRING -- mongodb://localhost:27017/
    MONGO_DATABASE_NAME -- article_management
    ENCRYPTION_FILE_PATH -- ./encryption_public_key.pem
    REDIS_CONNECTION_STRING -- redis://localhost:6379
    WORKER_COUNT -- 1 increase if needed

    ```

4. **Start the Service:**
    Run with auto migration and prod config
    ```bash
    python main.py --config=prod
    ```

## 🎯 To run Tests
   the article management microservice has quite high test coverage so before
   running start the test first
```bash
    CMD pytest
``` 

## 🎯 Key Endpoints

All primary endpoints in the Article Service require a valid, signed JWT for access control.

### 1. Health and Documentation

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/healthcheck` | Confirms the API is running and connected to the database. |

### 2. Article Management (CRUD)

| Method | Path | Name | Description | Requires Auth |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/articles` | `create_article` | Creates a new article entry. | **Yes** |
| `PUT` | `/api/v1/articles/{article_id}` | `update_article` | Updates an existing article by ID. | **Yes** |
| `DELETE` | `/api/v1/articles/{article_id}` | `delete_article` | Deletes an article by ID. | **Yes** |
| `GET` | `/api/v1/articles/{article_id}` | `get_article` | Retrieves a single article by ID. | **Yes** |
| `POST` | `/api/v1/articles/query` | `query_articles` | Performs a filtered search/query against articles (e.g., pagination, filtering). | **Yes** |

---

## 🔐 Authorization Flow

This service operates completely **statelessly** regarding authentication, relying entirely on the IAM Service's JWTs.

1.  **Client Request:** A client sends a request with a JWT in the `Authorization: Bearer <token>` header to the Article Service.
2.  **Verification:** The Article Service uses the **IAM's Public Key** (configured via `ENCRYPTION_FILE_PATH`) to immediately verify the token's signature.
3.  **Authorization:** Once the token is verified and the user's role/permissions are read from the JWT payload, the service applies its local can be found under src.security.auth **RBAC logic** 
    

---

## 💡 Architecture Notes

* **Role Delegation:** The **IAM Service** is the only one authorized to *issue* tokens. This service is only authorized to *consume* and verify them.
* **Decoupling:** By using **RS256** and the public key, the Article Service never needs to make a synchronous call back to the IAM Service to verify a token, ensuring high performance and resilience.
* **Data Isolation:** This microservice uses its own dedicated MongoDB database, ensuring separation of concerns from the IAM's user and role data.