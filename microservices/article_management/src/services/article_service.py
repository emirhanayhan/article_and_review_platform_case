from typing import Optional
from datetime import datetime
from bson import Decimal128

from src.repositories.article_repository import ArticleRepository
from src.models.articles import ArticleCreateModel, ArticleModel, ArticleUpdateModel
from src.models.users import UserModel
from src.security.exceptions import AppException


class ArticleService:
    def __init__(self, repo: ArticleRepository):
        self.repo = repo

    async def create_article(self, create_payload: ArticleCreateModel, current_user:UserModel) -> ArticleModel:
        create_payload = create_payload.model_dump()
        create_payload["created_by"] = current_user.id.hex
        create_payload["updated_by"] = current_user.id.hex

        article = ArticleModel(**create_payload)

        article_doc = article.model_dump()

        # this is how mongodb handles decimals
        article_doc["star_ratio"] = Decimal128(article_doc["star_ratio"])
        article_doc.pop("id", None)

        create_result = await self.repo.create(article_doc)
        article.id = str(create_result.inserted_id)
        return article

    async def get_article(self, article_id: str) -> Optional[ArticleModel]:
        article = await self.repo.get_by_id(article_id)
        if not article:
            raise AppException(
                error_message="article not found",
                error_code="exceptions.articleNotFound",
                status_code=404
            )
        article._id = article_id
        return article

    async def update_article(self, update_payload: ArticleUpdateModel, article_id: str, current_user:UserModel):
        update_payload = update_payload.model_dump(exclude_unset=True)
        update_payload["updated_by"] = current_user.id.hex
        update_payload["updated_at"] = datetime.utcnow()
        update_result = await self.repo.update(update_payload, article_id)
        if update_result.modified_count < 1 and update_result.matched_count >= 1:
            raise AppException(
                error_message="no changes on update",
                error_code="exceptions.exactSameDocument",
                status_code=409
            )
        return update_payload

    async def delete_article(self, article_id: str):
        delete_result = await self.repo.delete(article_id)
        if delete_result.deleted_count < 1:
            raise AppException(
                error_message="unable perform delete",
                status_code=409,
                error_code = "exceptions.unableToDelete",
            )
        return {}

    async def query_articles(self, query_parameters):
        result = await self.repo.query(
            query_parameters.skip, query_parameters.limit, query_parameters.filter,
            query_parameters.sort_by, query_parameters.sort_dir, query_parameters.select
        )
        return result
