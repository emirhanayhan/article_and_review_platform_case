import os
import pymongo
import logging
from bson import ObjectId
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def process_article_rating(rating, db):
    article_id = rating["_id"]
    avg_star = rating["avg_star"]
    count = rating["count"]

    logger.info("processing article : {}".format(article_id))
    update_result = db.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": {
            "star_ratio": avg_star,
            "review_count": count
        }}
    )
    if update_result.matched_count < 1:
        logger.info("article hard deleted")
    return article_id


def start_job():
    executor = ThreadPoolExecutor(max_workers=os.cpu_count())

    reviews_conn = os.getenv("REVIEWS_DATABASE_CONNECTION_STRING")
    articles_conn = os.getenv("ARTICLE_DATABASE_CONNECTION_STRING")

    reviews_db = pymongo.MongoClient(reviews_conn)["review_management"]
    articles_db = pymongo.MongoClient(articles_conn)["article_management"]

    reviews_repo = reviews_db["reviews"]
    articles_repo = articles_db["articles"]


    # NOTE this query should be okay for
    # tables has less than 1M documents
    # after that optimizations should be done
    pipeline = [
        {
            "$group": {
                "_id": "$article_id",
                "avg_star": {"$avg": "$star_ratio"},
                "count": {"$sum": 1}
            }
        }
    ]
    list(executor.map(process_article_rating, reviews_repo.aggregate(pipeline), repeat(articles_repo)))
    logger.info("job has finished")


if __name__ == "__main__":
    start_job()