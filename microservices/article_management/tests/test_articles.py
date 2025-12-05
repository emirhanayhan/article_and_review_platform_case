import pytest
import jwt
import uuid
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

from fastapi.testclient import TestClient

from src import create_fastapi_app
from configs.test import test_config

@pytest.fixture
def client():
    # test config for using test database
    app = create_fastapi_app(test_config)
    return TestClient(app)

def create_test_jwt(test_private_key_path, required_permissions):
    with open(test_private_key_path, "rb") as f:
        encryption_file = serialization.load_pem_private_key(f.read(), password=None)
        test_encryption_private_key = encryption_file.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # or use BestAvailableEncryption(b"password")
        )
        jwt_payload = {
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(seconds=9999),
            # can be used in future for single use jwt
            "jti": str(uuid.uuid4().hex),
            # random user_id
            "sub": str(uuid.uuid4().hex),
            # type --> access token
            "typ": "ac",
            "prm": required_permissions,
        }
        # generate access token
        access_token = jwt.encode(payload=jwt_payload, key=test_encryption_private_key, algorithm='RS256')
        return access_token, jwt_payload


@pytest.mark.asyncio
async def test_success_article_create(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(client.app.config["test_encryption_file_path"], ["create_article"])
        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

@pytest.mark.asyncio
async def test_success_article_update(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(client.app.config["test_encryption_file_path"], ["create_article", "update_article"])
        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        article_update_payload = {
            "status": "published"
        }

        response = client.put(f"api/v1/articles/{body["_id"]}", json=article_update_payload, headers=headers)
        body = response.json()
        assert response.status_code == 201
        assert body["updated_by"] == token_payload["sub"]
        assert body["status"] == "published"


@pytest.mark.asyncio
async def test_success_article_delete(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "delete_article"]
        )

        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]


        response = client.delete(f"api/v1/articles/{body["_id"]}", headers=headers)
        assert response.status_code == 204

@pytest.mark.asyncio
async def test_success_article_get(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "get_article"]
        )

        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]


        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        get_response_body = response.json()

        assert response.status_code == 200
        assert get_response_body["_id"] == body["_id"]

@pytest.mark.asyncio
async def test_success_article_query(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "query_articles"]
        )

        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        second_article_create_payload = {
            "title": "Buridan’s Principle",
            "author": "Leslie Lamport",
            "article_content": "https://dummy.cloudfront.net/assets/example2.pdf",
            "publish_date": "1984-10-01T00:00:00Z",
            "status": "published"
        }
        response = client.post("api/v1/articles", json=second_article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        article_query_payload = {
            "filter": {"status": "published"},
            "skip": 0,
            "select": ["_id", "created_at", "status"]
        }

        response = client.post("api/v1/articles/query", json=article_query_payload, headers=headers)
        query_body = response.json()

        assert response.status_code == 200
        assert query_body["count"] > 1
        # ensure documents don't have not selected field
        assert all([True for doc in query_body["docs"] if not doc.get("updated_at")])
        # ensure document has selected field
        assert all([True for doc in query_body["docs"] if doc.get("created_at")])
        # ensure filtering works properly
        assert all([True for doc in query_body["docs"] if doc.get("status") == "published"])

@pytest.mark.asyncio
async def test_success_article_get_cache(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "get_article"]
        )

        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]


        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        db_get_response_body = response.json()

        assert response.status_code == 200
        assert db_get_response_body["_id"] == body["_id"]

        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        cache_get_response_body = response.json()

        assert response.status_code == 200
        assert cache_get_response_body["_id"] == body["_id"]

        assert db_get_response_body == cache_get_response_body

@pytest.mark.asyncio
async def test_success_article_query_cache(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "query_articles"]
        )

        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        second_article_create_payload = {
            "title": "Buridan’s Principle",
            "author": "Leslie Lamport",
            "article_content": "https://dummy.cloudfront.net/assets/example2.pdf",
            "publish_date": "1984-10-01T00:00:00Z",
            "status": "published"
        }
        response = client.post("api/v1/articles", json=second_article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        article_query_payload = {
            "filter": {"status": "published"},
            "skip": 0,
            "select": ["_id", "created_at", "status"]
        }

        response = client.post("api/v1/articles/query", json=article_query_payload, headers=headers)
        db_query_body = response.json()

        assert response.status_code == 200
        assert db_query_body["count"] > 1
        # ensure documents don't have not selected field
        assert all([True for doc in db_query_body["docs"] if not doc.get("updated_at")])
        # ensure document has selected field
        assert all([True for doc in db_query_body["docs"] if doc.get("created_at")])
        # ensure filtering works properly
        assert all([True for doc in db_query_body["docs"] if doc.get("status") == "published"])

        response = client.post("api/v1/articles/query", json=article_query_payload, headers=headers)
        cache_query_body = response.json()
        assert response.status_code == 200
        assert db_query_body == cache_query_body

@pytest.mark.asyncio
async def test_success_article_update_cache(client):
    with client as client:
        article_create_payload = {
            "title": "A Relational Model of Data for Large Shared Data Banks",
            "author": "Edgar F. Codd",
            "article_content": "https://dummy.cloudfront.net/assets/example.pdf",
            "publish_date": "1970-06-01T00:00:00Z",
            "status": "draft"
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_article", "update_article", "get_article"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        response = client.post("api/v1/articles", json=article_create_payload, headers=headers)
        body = response.json()

        assert response.status_code == 201
        assert "_id" in body
        assert "title" in body
        assert "created_at" in body
        assert "updated_at" in body
        assert body["star_ratio"] == "0.0"
        assert body["created_by"] == token_payload["sub"]

        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        # send second time to ensure cached
        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        before_update_get_response_body = response.json()

        article_update_payload = {
            "status": "published"
        }

        response = client.put(f"api/v1/articles/{body["_id"]}", json=article_update_payload, headers=headers)
        update_body = response.json()
        assert response.status_code == 201
        assert update_body["updated_by"] == token_payload["sub"]
        assert update_body["status"] == "published"

        response = client.get(f"api/v1/articles/{body["_id"]}", headers=headers)
        after_update_get_response_body = response.json()

        assert after_update_get_response_body["status"] == "published"
        assert after_update_get_response_body != before_update_get_response_body
