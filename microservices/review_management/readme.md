# ⭐ Review Management Microservice
Review management microservice 

---

## 🚀 Getting Started

### Prerequisites

* Python 3.13
* MongoDB 4.4
* Redis 7.1

### Setup


1**Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2**Environment Variables:**
    Project can be started with local configuration without settings. The following environment variables are expected for production/staging:

    ```env
    ENV -- DEFAULT (only on local configuration)
    HOST -- 0.0.0.0
    PORT -- 8000
    # Connection string for the Review database
    MONGO_CONNECTION_STRING -- mongodb://localhost:27017/
    MONGO_DATABASE_NAME -- review_management
    ENCRYPTION_FILE_PATH -- ./encryption_public_key.pem
    REDIS_CONNECTION_STRING -- redis://localhost:6379
    ARTICLE_SERVICE_BASE_URL -- http://localhost:8001
    WORKER_COUNT -- 1 increase if needed
    
    ```

3**Start the Service:**
    Run
    ```bash
    python main.py --config=prod
    ```

---

## 🎯 To run Tests
   the article management microservice has quite high test coverage so before
   running start the test first
```bash
    CMD pytest
``` 

## 🎯 Key Endpoints

All primary endpoints in the Review Service require a valid, signed JWT for access control. This service often requires additional **ownership checks** (e.g., only the user who created a review can update or delete it).

### 1. Health and Documentation

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/healthcheck` | Confirms the API is running and connected to the database. |


### 2. Review Management (CRUD)

| Method | Path | Name | Description | Requires Auth |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/reviews` | `create_review` | Creates a new review for an article or product. | **Yes** |
| `PUT` | `/api/v1/reviews/{review_id}` | `update_review` | Modifies an existing review by ID (often requires ownership). | **Yes** |
| `DELETE` | `/api/v1/reviews/{review_id}` | `delete_review` | Deletes a review by ID (requires ownership or Admin role). | **Yes** |
| `GET` | `/api/v1/reviews/{review_id}` | `get_review` | Retrieves a single review by ID. | **Yes** |
| `POST` | `/api/v1/reviews/query` | `query_reviews` | Searches or filters reviews (e.g., by article ID, user ID, or rating). | **Yes** |

---