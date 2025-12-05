from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from cryptography.hazmat.primitives import serialization

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from src.api.healthcheck import init_healthcheck_api
from src.api.me import init_me_api
from src.api.users import init_users_api
from src.api.tokens import init_tokens_api
from src.api.roles import init_roles_api
from src.security.exceptions import init_exception_handler


@asynccontextmanager
async def lifespan(app):

    # this will use to encrypt jwts
    with open(app.config["encryption_file_path"], "rb") as f:
        encryption_file = serialization.load_pem_private_key(f.read(), password=None)
        app.encryption_public_key = encryption_file.public_key()
        app.encryption_private_key = encryption_file.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # or use BestAvailableEncryption(b"password")
        )

    # init postgres client
    pg_engine = create_async_engine(app.config["postgres_connection_string"])
    app.pg_session = sessionmaker(bind=pg_engine, class_=AsyncSession, expire_on_commit=False)

    # run migrations if option --migrate=true given
    if app.config.get("run_migrations"):
        from src.models.users import UserModel
        from src.models.roles import RoleModel
        async with pg_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

    # for cpu bound tasks to not block api
    # not forget the use it with asyncio.wrap_future
    # otherwise still blocks event loop
    app.thread_pool = ThreadPoolExecutor()

    yield


def create_fastapi_app(settings):
    app = FastAPI(lifespan=lifespan)
    app.config = settings

    init_exception_handler(app)

    # init apis
    init_healthcheck_api(app)
    init_users_api(app)
    init_tokens_api(app)
    init_roles_api(app)
    init_me_api(app)

    return app