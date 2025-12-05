import hashlib
import json
from typing import Optional, Dict, Any
from decimal import Decimal

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId, Decimal128
from src.models.reviews import ReviewModel

# TTLs in seconds
ENTITY_TTL = 300  # cached single-review (5 minutes)
QUERY_TTL = 30  # cached query results (30 seconds)


def _normalize_for_cache(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert non-JSON serializable types into JSON-friendly ones
    - ObjectId -> str
    - Decimal128 -> float (or str if you prefer)
    """
    if not doc:
        return doc

    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, Decimal128):
            out[k] = float(v.to_decimal())
        elif isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out


def _prepare_doc_for_model(doc) -> Dict[str, Any]:
    """
    Prepare DB doc for ReviewModel construction:
    - convert Decimal128 -> Decimal
    - convert _id to id or remove (depends on your model)
    """
    if "_id" in doc:
        # If your model expects id field (not _id), map it
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)

    if "star_ratio" in doc and isinstance(doc["star_ratio"], Decimal128):
        doc["star_ratio"] = doc["star_ratio"].to_decimal()

    return doc


def fingerprint(key_data: dict) -> str:
    """Stable hash for query cache keys."""
    raw = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


class ReviewRepository:
    def __init__(self, db: AsyncIOMotorDatabase, cache):
        self.collection = db["reviews"]
        self.cache = cache

    async def create(self, review_doc):
        result = await self.collection.insert_one(review_doc)
        await self.cache.delete_pattern("review:query:*")
        # todo maybe consider caching after create
        return result

    async def get_by_id(self, review_id: str):
        cache_key = f"review:id:{review_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            cached = dict(cached)
            if "star_ratio" in cached:
                try:
                    cached["star_ratio"] = Decimal(str(cached["star_ratio"]))  # noqa
                except KeyError:
                    pass
            return ReviewModel(**cached)

        doc = await self.collection.find_one({"_id": ObjectId(review_id)})
        if not doc:
            return None

        doc = _prepare_doc_for_model(doc)
        # todo fix this weird approach caused by pydantic :/
        _id = doc.pop("id")
        model = ReviewModel(**doc)
        model._id = _id
        await self.cache.set(cache_key, _normalize_for_cache(jsonable_encoder(model)), ttl=ENTITY_TTL)
        return model

    async def update(self, update_payload, review_id: str):
        updated = await self.collection.update_one({"_id": ObjectId(review_id)}, {"$set": update_payload})
        await self.cache.delete(f"review:id:{review_id}")
        await self.cache.delete_pattern("review:query:*")

        return updated

    async def delete(self, review_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(review_id)})

        await self.cache.delete(f"review:id:{review_id}")
        await self.cache.delete_pattern("review:query:*")
        return result

    async def query(self, skip, limit, _filter, sort_by, sort_dir, select):
        key_data = {
            "skip": skip,
            "limit": limit,
            "filter": _filter,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
            "select": select,
        }
        cache_key = f"review:query:{fingerprint(key_data)}"

        # check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        mongo_filter = {}

        if _filter:
            mongo_filter = {
                key: ObjectId(value) if key == "_id" else value
                for key, value in _filter.items()
            }

        projection = None
        if select:
            projection = {field: 1 for field in select}
            if "id" in projection and "_id" not in projection:
                projection["_id"] = 1
                del projection["id"]

        cursor = self.collection.find(mongo_filter, projection=projection)

        if sort_by:
            cursor = cursor.sort(sort_by, sort_dir)

        cursor = cursor.skip(skip).limit(limit)

        docs = await cursor.to_list(length=limit)

        payload = {"count": len(docs), "docs": docs}
        await self.cache.set(cache_key, payload, ttl=QUERY_TTL)

        return payload