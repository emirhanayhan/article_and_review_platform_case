from fastapi import Request

def init_healthcheck_api(app):
    @app.get("/api/v1/healthcheck")
    async def healthcheck(request: Request):
        # can be used for kubernetes readiness probe
        # if something is wrong on api or db layer
        # deployment will shown as Unhealthy

        # mongodb ping
        await request.app.db.client.admin.command('ping')

        return {"status": "healthy"}
