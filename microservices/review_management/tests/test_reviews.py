import pytest
import jwt
import uuid
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization

from fastapi.testclient import TestClient
from aioresponses import aioresponses

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
async def test_success_review_create(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(client.app.config["test_encryption_file_path"], ["create_review", "get_article"])
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()

        assert response.status_code == 201
        assert body["created_by"] == token_payload["sub"]
        assert body["review_content"] == "I enjoyed this article"
        assert body["star_ratio"] == 4
        assert body["article_id"] == dummy_id

@pytest.mark.asyncio
async def test_success_review_update(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "update_review", "get_article"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()

        assert response.status_code == 201
        assert body["created_by"] == token_payload["sub"]
        assert body["review_content"] == "I enjoyed this article"
        assert body["star_ratio"] == 4
        assert body["article_id"] == dummy_id

        review_update_payload = {
            "review_content": "I do not enjoyed this article",
            "star_ratio": 2,
        }
        response = client.put(f"api/v1/reviews/{body["_id"]}", json=review_update_payload, headers=headers)

        update_body = response.json()

        assert response.status_code == 201
        assert update_body["review_content"] == "I do not enjoyed this article"
        assert update_body["star_ratio"] == 2
        assert update_body["updated_by"] == token_payload["sub"]

@pytest.mark.asyncio
async def test_success_review_delete(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "delete_review"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()

        assert response.status_code == 201
        assert body["created_by"] == token_payload["sub"]
        assert body["review_content"] == "I enjoyed this article"
        assert body["star_ratio"] == 4
        assert body["article_id"] == dummy_id

        response = client.delete(f"api/v1/reviews/{body["_id"]}", headers=headers)

        assert response.status_code == 204

@pytest.mark.asyncio
async def test_success_review_get(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "get_review"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()

        assert response.status_code == 201
        assert body["created_by"] == token_payload["sub"]
        assert body["review_content"] == "I enjoyed this article"
        assert body["star_ratio"] == 4
        assert body["article_id"] == dummy_id

        response = client.get(f"api/v1/reviews/{body["_id"]}", headers=headers)
        get_body = response.json()

        assert response.status_code == 200
        assert get_body["_id"] == body["_id"]
        assert get_body["created_by"] == token_payload["sub"]
        assert get_body["review_content"] == "I enjoyed this article"
        assert get_body["star_ratio"] == 4
        assert get_body["article_id"] == dummy_id

@pytest.mark.asyncio
async def test_success_review_query(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "get_review", "query_reviews"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()

        assert response.status_code == 201
        assert body["created_by"] == token_payload["sub"]
        assert body["review_content"] == "I enjoyed this article"
        assert body["star_ratio"] == 4
        assert body["article_id"] == dummy_id

        reviews_query_payload = {
            "filter": {"star_ratio": 4},
            "skip": 0,
            "select": ["_id", "created_at", "star_ratio"]
        }

        response = client.post("api/v1/reviews/query", json=reviews_query_payload, headers=headers)
        query_body = response.json()

        assert response.status_code == 200
        assert query_body["count"] > 1
        # ensure documents don't have not selected field
        assert all([True for doc in query_body["docs"] if not doc.get("updated_at")])
        # ensure document has selected field
        assert all([True for doc in query_body["docs"] if doc.get("created_at")])
        # ensure filtering works properly
        assert all([True for doc in query_body["docs"] if doc.get("star_ratio") == 4])

@pytest.mark.asyncio
async def test_success_review_get_cache(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "get_review", "query_reviews"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

        body = response.json()
        assert response.status_code == 201

        response = client.get(f"api/v1/reviews/{body["_id"]}", headers=headers)
        db_get_body = response.json()
        assert response.status_code == 200

        response = client.get(f"api/v1/reviews/{body["_id"]}", headers=headers)
        cache_get_body = response.json()
        assert response.status_code == 200
        assert db_get_body == cache_get_body

@pytest.mark.asyncio
async def test_success_review_query_cache(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "get_review", "query_reviews"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200, repeat=True)

            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)

            body = response.json()
            assert response.status_code == 201
            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)
            body = response.json()
            assert response.status_code == 201

        reviews_query_payload = {
            "filter": {"star_ratio": 4},
            "skip": 0,
            "select": ["_id", "created_at", "star_ratio"]
        }

        response = client.post("api/v1/reviews/query", json=reviews_query_payload, headers=headers)
        db_query_body = response.json()

        assert response.status_code == 200
        assert db_query_body["count"] > 1
        # ensure documents don't have not selected field
        assert all([True for doc in db_query_body["docs"] if not doc.get("updated_at")])
        # ensure document has selected field
        assert all([True for doc in db_query_body["docs"] if doc.get("created_at")])
        # ensure filtering works properly
        assert all([True for doc in db_query_body["docs"] if doc.get("star_ratio") == 4])

        response = client.post("api/v1/reviews/query", json=reviews_query_payload, headers=headers)
        cache_query_body = response.json()

        assert response.status_code == 200
        assert cache_query_body == db_query_body

@pytest.mark.asyncio
async def test_success_review_update_cache(client):
    with client as client:
        dummy_id = "69317e3113dd24d5bfc70e44"
        review_create_payload = {
            "article_id": dummy_id,
            "review_content" : "I enjoyed this article",
            "star_ratio" : 4,
        }
        token, token_payload = create_test_jwt(
            client.app.config["test_encryption_file_path"],
            ["create_review", "get_article", "get_review", "update_review"]
        )
        headers = {
            "Authorization": "Bearer " + token
        }
        with aioresponses() as mocker:
            # mock response from article service
            mock_url = f'{client.app.config["article_service_base_url"]}/api/v1/articles/{dummy_id}'
            mocker.get(mock_url, payload={"_id": "69317e3113dd24d5bfc70e44"}, status=200, repeat=True)
            response = client.post("api/v1/reviews", json=review_create_payload, headers=headers)
        body = response.json()
        assert response.status_code == 201

        review_update_payload = {
            "review_content": "I do not enjoyed this article",
            "star_ratio": 2,
        }
        response = client.put(f"api/v1/reviews/{body["_id"]}", json=review_update_payload, headers=headers)

        update_body = response.json()
        
        response = client.get(f"api/v1/reviews/{body["_id"]}", headers=headers)
        db_get_body_after_update = response.json()
        assert response.status_code == 200

        response = client.get(f"api/v1/reviews/{body["_id"]}", headers=headers)
        cache_get_body_after_update = response.json()
        assert response.status_code == 200
        assert db_get_body_after_update == cache_get_body_after_update
        assert db_get_body_after_update["star_ratio"] == 2
        assert cache_get_body_after_update["star_ratio"] == 2
