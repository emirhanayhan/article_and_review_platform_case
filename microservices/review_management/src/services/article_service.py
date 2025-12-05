import aiohttp
from src.security.exceptions import AppException

class ArticleService:
    def __init__(self, base_url):
        self.base_url = base_url

    async def get(self, article_id, auth_token):
        url = f"{self.base_url}/api/v1/articles/{article_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"Authorization": auth_token}) as response:
                if response.status == 404:
                    raise AppException(
                        error_message="article not found",
                        error_code="exceptions.articleNotFound",
                        status_code=404
                    )
                elif response.status in [401, 403]:
                    raise AppException(
                        error_message="unauthorized",
                        error_code="exceptions.unauthorizedForAction",
                        status_code=401
                    )
                elif response.status == 200:
                    return await response.json()

                # unexpected status code something wrong with article microservice
                else:
                    raise AppException(
                        status_code=503,
                        error_message="internal server error",
                        error_code="exceptions.articleInternalServerError",
                    )
