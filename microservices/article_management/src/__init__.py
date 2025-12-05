from contextlib import asynccontextmanager
from cryptography.hazmat.primitives import serialization

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from src.api.healthcheck import init_healthcheck_api
from src.api.articles import init_articles_api
from src.repositories.article_repository import ArticleRepository
from src.repositories.cache_repository import CacheRepository
from src.services.article_service import ArticleService
from src.security.exceptions import init_exception_handler


@asynccontextmanager
async def lifespan(app):

    # init mongo client
    db_client = AsyncIOMotorClient(app.config["mongo_connection_string"], retryWrites=True)
    app.db = db_client[app.config["mongo_database_name"]]

    # init services
    cache_repository = CacheRepository(app.config["redis_connection_string"])
    article_repo = ArticleRepository(app.db, cache_repository)
    app.article_service = ArticleService(article_repo)

    # this will use to verify jwts
    with open(app.config["encryption_file_path"], "rb") as f:
        public_key_file = serialization.load_pem_public_key(f.read())
        app.public_key = public_key_file.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    yield


def create_fastapi_app(settings):
    app = FastAPI(lifespan=lifespan)
    app.config = settings

    # init custom exception handler
    init_exception_handler(app)

    # init apis
    init_healthcheck_api(app)
    init_articles_api(app)

    return app