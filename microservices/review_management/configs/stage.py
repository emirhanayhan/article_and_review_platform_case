from os import getenv

stage_config = {
    "config": "stage",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "mongo_connection_string": getenv("MONGO_CONNECTION_STRING"),
    "mongo_database_name": getenv("MONGO_DATABASE_NAME"),
    "encryption_file_path": getenv("ENCRYPTION_FILE_PATH"),
    "redis_connection_string": getenv("REDIS_CONNECTION_STRING"),
    "article_service_base_url": getenv("ARTICLE_SERVICE_BASE_URL"),
}
