from os import getenv

# this configuration has default values set
local_config = {
    "config": "local",
    "host": getenv("HOST", "0.0.0.0"),
    "port": int(getenv("PORT", "8000")),
    "postgres_connection_string": "postgresql+asyncpg://ea:123123@db:5432/iam_test",
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    # in seconds 5 days
    "refresh_token_ttl": int(getenv("REFRESH_TOKEN_TTL", "432000")),
    # in seconds 1 day
    "access_token_ttl": int(getenv("ACCESS_TOKEN_TTL", "86400")),
    "encryption_file_path":getenv("ENCRYPTION_FILE_PATH", "./encryption_private_key.pem")
}