from os import getenv

test_config = {
    "config": "test",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "postgres_connection_string": "postgresql+asyncpg://0.0.0.0:5432/iam_test",
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    # in seconds 5 days
    "refresh_token_ttl": int(getenv("REFRESH_TOKEN_TTL", "9999999")),
    # in seconds 1 day
    "access_token_ttl": int(getenv("ACCESS_TOKEN_TTL", "9999999")),
    "encryption_file_path":getenv("ENCRYPTION_FILE_PATH", "../encryption_private_key.pem")
}