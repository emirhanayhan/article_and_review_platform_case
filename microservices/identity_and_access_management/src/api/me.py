import jwt
from fastapi import Request
from sqlmodel import select

from src.models.users import UserModel
from src.security.exceptions import AppException


def init_me_api(app):
    @app.get("/api/v1/me", status_code=200)
    async def get_me(request: Request):
        if not request.headers["authorization"].startswith("Bearer "):
            raise AppException(
                error_message="Invalid Token Type",
                error_code="exceptions.invalidTokenType",
                status_code=401
            )
        auth_token = request.headers["authorization"].split("Bearer ")[1]

        decoded_unverified = jwt.decode(auth_token, algorithms="RS256", options={"verify_signature": False})
        if decoded_unverified.get("typ") != "ac":
            raise AppException(
                error_message="invalid token type",
                error_code="exceptions.invalidTokenType",
                status_code=401
            )
        async with request.app.pg_session() as session:
            user = (await session.exec(select(UserModel).where(UserModel.id == decoded_unverified["sub"]))).first()
            if not user:
                raise AppException(
                    error_message="User not found",
                    error_code="exceptions.userNotFound",
                    status_code=404
                )
        verified_decoded = jwt.decode(auth_token, key=request.app.encryption_public_key, algorithms="RS256", options={"verify_signature": True, "verify_exp": True})
        del user.password

        return user
        