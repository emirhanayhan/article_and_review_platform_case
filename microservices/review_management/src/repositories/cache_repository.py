import json
import redis.asyncio
from typing import Any, Optional, List
from bson import ObjectId

from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError ("Type %s not serializable" % type(obj))


class CacheRepository:
    def __init__(self, url, encoding: str = "utf-8"):
        self._redis = redis.asyncio.from_url(url, encoding=encoding, decode_responses=True)

    async def get(self, key: str) -> Optional[Any]:
        data = await self._redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 60) -> None:
        """Store JSON-serializable value with TTL (seconds)."""
        await self._redis.set(key, json.dumps(value, default=json_serial), ex=ttl)

    async def delete(self, *keys: str) -> None:
        if not keys:
            return
        await self._redis.delete(*keys)

    async def scan_keys(self, pattern: str, count: int = 100) -> List[str]:
        """Return list of keys matching pattern using SCAN (non-blocking)."""
        cur = b"0"
        found: List[str] = []
        # aioredis scan returns (cursor, keys)
        while True:
            cur, keys = await self._redis.scan(cur, match=pattern, count=count)
            if keys:
                found.extend(keys)
            if cur == 0 or cur == b"0":
                break
        return found

    async def delete_pattern(self, pattern: str) -> None:
        """Delete keys matching pattern safely using SCAN/DEL."""
        keys = await self.scan_keys(pattern)
        if keys:
            # chunk deletes to avoid overload
            chunk = 100
            for i in range(0, len(keys), chunk):
                await self._redis.delete(*keys[i : i + chunk])

    async def close(self) -> None:
        await self._redis.close()