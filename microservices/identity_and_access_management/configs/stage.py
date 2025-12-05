from os import getenv

stage_config = {
    "config": "stage",
    "host": getenv("HOST"),
    "port": int(getenv("PORT", "8000")),
    "postgres_connection_string": getenv("POSTGRES_CONNECTION_STRING"),
    "worker_count": int(getenv("WORKER_COUNT", "1")),
    "refresh_token_ttl": int(getenv("REFRESH_TOKEN_TTL", "432000")),
    "access_token_ttl": int(getenv("ACCESS_TOKEN_TTL", "86400")),
    "encryption_file_path":getenv("ENCRYPTION_FILE_PATH")
}
