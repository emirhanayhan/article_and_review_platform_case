from fastapi import Request

from src.models.roles import RoleModel


def init_roles_api(app):
    @app.post("/api/v1/roles", status_code=201)
    async def create_role(role: RoleModel, request: Request):
        async with request.app.pg_session() as session:
            # safe store password
            session.add(role)
            await session.commit()

        return role