import jwt
from fastapi import Request

from src.security.exceptions import AppException
from src.models.users import UserModel


async def authenticate_and_authorize(rq: Request):
    # TODO add wildcard logic

    # action like create_article
    # required permission to access this endpoint
    required_permission =  rq.scope["route"].name

    if not rq.headers.get("authorization", "").startswith("Bearer "):
        raise AppException(
            error_message="invalid authorization header",
            error_code="exceptions.invalidAuthorizationHeader",
            status_code=401
        )

    token = rq.headers.get("authorization").split("Bearer ")[1]

    decoded = jwt.decode(token, algorithms="RS256", options={"verify_signature": False})
    if decoded.get("typ") != "ac":
        raise AppException(
            error_message="invalid token type",
            error_code="exceptions.invalidTokenType",
            status_code=401
        )

    verified_decoded = jwt.decode(token, key=rq.app.public_key, algorithms="RS256", options={"verify_signature": True, "verify_exp": True})
    if required_permission not in verified_decoded["prm"]:
        raise AppException(
            error_message="User has no permission take this action",
            error_code="exceptions.userNotAuthorized",
            status_code=403
        )

    return UserModel(id=verified_decoded["sub"], permissions=verified_decoded["prm"])
