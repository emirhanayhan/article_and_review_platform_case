from os import getenv

# this configuration has default values set
local_config = {
    "config": "local",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "mongo_connection_string": getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/"),
    "mongo_database_name": getenv("MONGO_DATABASE_NAME", "review_management"),
    "encryption_file_path": getenv("ENCRYPTION_FILE_PATH", "./encryption_public_key.pem"),
    "redis_connection_string": getenv("REDIS_CONNECTION_STRING", "redis://localhost:6379"),
    "article_service_base_url": getenv("ARTICLE_SERVICE_BASE_URL", "http://localhost:8001"),
}
