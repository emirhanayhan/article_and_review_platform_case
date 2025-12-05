from os import getenv

prod_config = {
    "config": "prod",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "mongo_connection_string": getenv("MONGO_CONNECTION_STRING"),
    "mongo_database_name": getenv("MONGO_DATABASE_NAME"),
    "encryption_file_path": getenv("ENCRYPTION_FILE_PATH"),
    "redis_connection_string": getenv("REDIS_CONNECTION_STRING"),
}
