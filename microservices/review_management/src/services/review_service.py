from bson import Decimal128
from datetime import datetime

from src.models.reviews import ReviewModel, ReviewCreateModel, ReviewUpdateModel
from src.models.users import UserModel
from src.security.exceptions import AppException


class ReviewService:
    def __init__(self, repo):
        self.repo = repo

    async def create_review(self, create_payload: ReviewCreateModel, current_user:UserModel):
        create_payload = create_payload.model_dump()
        create_payload["created_by"] = current_user.id.hex
        create_payload["updated_by"] = current_user.id.hex

        review = ReviewModel(**create_payload)

        review_doc = review.model_dump()
        review_doc.pop("id", None)

        create_result = await self.repo.create(review_doc)
        review.id = str(create_result.inserted_id)
        return review


    async def get_review(self, review_id: str):
        review = await self.repo.get_by_id(review_id)
        if not review:
            raise AppException(
                error_message="review not found",
                error_code="exceptions.reviewNotFound",
                status_code=404
            )
        review._id = review_id
        return review

    async def update_review(self, update_payload: ReviewUpdateModel, review_id: str, current_user:UserModel):
        update_payload = update_payload.model_dump(exclude_unset=True)
        update_payload["updated_by"] = current_user.id.hex
        update_payload["updated_at"] = datetime.utcnow()
        update_result = await self.repo.update(update_payload, review_id)
        if update_result.modified_count < 1 and update_result.matched_count >= 1:
            raise AppException(
                error_message="no changes on update",
                error_code="exceptions.exactSameDocument",
                status_code=409
            )
        return update_payload

    async def delete_review(self, review_id: str):
        delete_result = await self.repo.delete(review_id)
        if delete_result.deleted_count < 1:
            raise AppException(
                error_message="unable perform delete",
                status_code=409,
                error_code = "exceptions.unableToDelete",
            )
        return {}

    async def query_reviews(self, query_parameters):
        result = await self.repo.query(
            query_parameters.skip, query_parameters.limit, query_parameters.filter,
            query_parameters.sort_by, query_parameters.sort_dir, query_parameters.select
        )
        return result