from os import getenv

test_config = {
    "config": "test",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "mongo_connection_string":  "mongodb://localhost:27017/",
    "mongo_database_name": "article_management_test",
    "encryption_file_path": getenv("ENCRYPTION_FILE_PATH", "../encryption_public_key.pem"),
    "test_encryption_file_path": "encryption_private_key.pem",
    "redis_connection_string": "redis://localhost:6379"
}