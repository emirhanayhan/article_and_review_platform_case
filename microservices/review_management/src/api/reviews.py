from fastapi import Request, Depends

from src.models.reviews import ReviewCreateModel, ReviewUpdateModel
from src.models import to_jsonable, QueryParamsModel
from src.security.auth import authenticate_and_authorize

def init_reviews_api(app):
    @app.post("/api/v1/reviews", status_code=201)
    async def create_review(request: Request, review: ReviewCreateModel, current_user = Depends(authenticate_and_authorize)):
        article = await request.app.article_service.get(review.article_id, request.headers.get("Authorization"))

        review = await request.app.review_service.create_review(review, current_user)
        return review

    @app.put("/api/v1/reviews/{review_id}", status_code=201)
    async def update_review(
            request: Request, review_update: ReviewUpdateModel,
            review_id: str,
            current_user = Depends(authenticate_and_authorize),
    ):
        review = await request.app.review_service.get_review(review_id)
        updated_review = await request.app.review_service.update_review(
            review_update, review_id, current_user
        )
        return updated_review

    @app.delete("/api/v1/reviews/{review_id}", status_code=204)
    async def delete_review(
            request: Request,
            review_id: str,
            current_user = Depends(authenticate_and_authorize),
    ):
        review = await request.app.review_service.get_review(review_id)

        deleted = await request.app.review_service.delete_review(review_id)

        return {}

    @app.get("/api/v1/reviews/{review_id}", status_code=200)
    async def get_review(
            request: Request,
            review_id: str,
            current_user = Depends(authenticate_and_authorize),
    ):
        review = await request.app.review_service.get_review(review_id)
        payload = review.model_dump()
        payload["_id"] = review_id
        return payload

    @app.post("/api/v1/reviews/query", status_code=200)
    async def query_reviews(
            request: Request, query_params: QueryParamsModel,
            current_user = Depends(authenticate_and_authorize)
    ):
        documents = await request.app.review_service.query_reviews(query_params)

        return to_jsonable(documents)
