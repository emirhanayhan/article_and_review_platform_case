import pytest

from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

from src import create_fastapi_app
from configs.test import test_config

@pytest.fixture
def client():
    # test config has test database
    app = create_fastapi_app(test_config)
    return TestClient(app)

@pytest.mark.asyncio
async def test_success_user_create(client):
    with client as client:
        # migrate test database
        from src.models.users import UserModel
        from src.models.roles import RoleModel

        pg_engine = create_async_engine(client.app.config["postgres_connection_string"])
        async with pg_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)


        role_payload = {"name": "test_role", "permissions": ["articles_create"]}
        response = client.post("api/v1/roles", json=role_payload)

        assert response.status_code == 201

        user_payload = {
            "full_name": "johnie walker",
            "email": "johniewalker@gmail.com",
            "password": "123123123",
            "role_id": "test_role"
        }
        response = client.post("/api/v1/users", json=user_payload)

        assert response.status_code == 201

        # teardown test database
        async with pg_engine.begin() as connection:
            await connection.execute(text('DROP TABLE IF EXISTS users CASCADE;'))
            await connection.execute(text('DROP TABLE IF EXISTS roles CASCADE;'))

