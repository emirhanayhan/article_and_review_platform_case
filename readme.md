# 🏛️ Microservices Study Case: Content and Review Platform

This project demonstrates a microservice architecture built with Python (FastAPI, SQLModel, PyMongo), deployed using Docker. It features a complete authorization flow (RBAC with JWTs) and scheduled background processing.

---

## 🎯 Architecture Overview

The system consists of **four distinct microservices** and three dedicated databases, communicating directly via HTTP and sharing a distributed cache.
system design diagram can be found under system_design.svg

### Key Components

* **IAM (Identity & Access Management):** Source of truth for users and roles.
* **Article Management:** Handles content CRUD and storage.
* **Review Management:** Handles user reviews and ratings.
* **Background Worker:** Executes daily scheduled aggregation tasks.

### Data Storage

| Service                | Primary Database | Caching/Secondary Store |
|:-----------------------| :--- | :--- |
| **IAM**                | PostgreSQL | None |
| **Article Management** | MongoDB | Distributed Redis Cluster |
| **Review Management**  | MongoDB | Distributed Redis Cluster |
| **Background Worker**  | Accesses Article/Review MongoDBs | None |

### Distributed Cache Algorithms and configurations

The Article and Review microservices share a single, distributed Redis instance to cache frequently accessed query results and reduce load on the MongoDB databases.
1. Distributed Cache Configuration

The Redis instance is configured to a fixed size and uses a mandatory eviction policy to manage the limit and maintain performance.

    Max Memory Limit: 1024 MB (Fixed Size)

    Eviction Policy: allkeys-lru (Least Recently Used)

This configuration ensures that when the 1024 MB memory limit is reached,
the Redis server automatically removes the least recently used keys across all namespaces to make room for new, fresh query results.
2. Caching Algorithm

Both the Article and Review services implement a Cache-Aside Pattern focusing on caching complex query results.
Element	Description	Purpose
Key Naming	Keys are namespaced to avoid conflicts:
entity:query_hash. (e.g., article:query:a1b2c3d4)	Ensures the Article service cannot
accidentally overwrite a Review service key.
Cached Data	The entire JSON response body or result set of the
last executed queries are stored.
Reduces latency by skipping MongoDB entirely for repeat queries.
Eviction Policy	Managed by the Redis server via allkeys-lru.	Automatically keeps the most popular/recently used query results in the 1024 MB cache.
Time-to-Live (TTL)	Every cached entry is assigned a short, explicit TTL (e.g., 5-15 minutes).	Guarantees eventual data consistency and prevents the cache from holding stale data forever.
Summary of Service Behavior

*** TTLS
QUERY = 30 SEC
ENTITY = 300 SEC

** Config
Caching Methodology = Cache-aside
Approach = fixed size distributed cache lru eviction


For every complex read operation, the microservice (Article or Review) will:

    Generate a unique key based on the query parameters.
    Check Redis for the key.
    On Hit: Return the cached data instantly.
    On Miss: Fetch data from MongoDB, save the result to Redis (with a TTL), and return the data.


### Communication Pattern

All external client traffic and internal service-to-service communication is handled via **direct HTTP calls**. Authentication relies on stateless **JWT verification** using a shared public key.

---

## 🚀 Getting Started

This guide will get the entire multi-service environment running locally using Docker Compose.

### Prerequisites

* **Docker**
* **Docker Compose** 

### 1. Build and Run the Services

Navigate to the project root directory where docker-compose.yml exists

```bash
docker compose up --build -d
```

## Endpoint Details
option 1-) Endpoint details can be found under microservice_directory/readme.md
option 2-) example swagger api address http://localhost:8000/docs

### Testing microservices
```bash
   pytest # will automatically locate tests in tests directory
```

For testing purposes projects have private keys under test directory
also public key for verification and private key for creating tokens 
can be found in root directory in related services private=IAM, public=Article&Review-Management

## Version Control Note
since each microservice developed independently this main project
has no commit history