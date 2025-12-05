from fastapi import Request, Depends

from src.models.articles import ArticleCreateModel, ArticleUpdateModel
from src.models import QueryParamsModel, to_jsonable

from src.security.auth import authenticate_and_authorize


def init_articles_api(app):
    @app.post("/api/v1/articles", status_code=201)
    async def create_article(request: Request, article: ArticleCreateModel, current_user = Depends(authenticate_and_authorize)):
        article = await request.app.article_service.create_article(article, current_user)

        return article

    @app.put("/api/v1/articles/{article_id}", status_code=201)
    async def update_article(
            request: Request, article_update: ArticleUpdateModel,
            article_id: str, current_user = Depends(authenticate_and_authorize)
    ):
        article = await request.app.article_service.get_article(article_id)

        updated_article = await request.app.article_service.update_article(
            article_update, article_id, current_user
        )
        return updated_article

    @app.delete("/api/v1/articles/{article_id}", status_code=204)
    async def delete_article(
            request: Request,
            article_id: str, current_user = Depends(authenticate_and_authorize)
    ):
        article = await request.app.article_service.get_article(article_id)

        deleted = await request.app.article_service.delete_article(article_id)

        return {}

    @app.get("/api/v1/articles/{article_id}", status_code=200)
    async def get_article(
            request: Request,
            article_id: str, current_user = Depends(authenticate_and_authorize)
    ):
        article = await request.app.article_service.get_article(article_id)
        payload = article.model_dump()
        # Note this id complexity caused by pydantic
        payload["_id"] = article._id
        return payload

    @app.post("/api/v1/articles/query", status_code=200)
    async def query_articles(
            request: Request, query_params: QueryParamsModel,
            current_user = Depends(authenticate_and_authorize)
    ):
        documents = await request.app.article_service.query_articles(query_params)

        return to_jsonable(documents)