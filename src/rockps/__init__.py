import fastapi
from fastapi import middleware as fa_middleware
from fastapi.middleware import cors

from rockps import adapters
from rockps import infrastructure


def init() -> fastapi.FastAPI:
    # Configures app

    app = fastapi.FastAPI(
        middleware=[
            fa_middleware.Middleware(
                cors.CORSMiddleware,
                allow_origins=[
                    "http://localhost",
                    "http://localhost:3000",
                    "http://localhost:8080",
                ],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
    )

    @app.middleware("http")
    async def global_middleware(request: fastapi.Request, handler):
        try:
            return await handler(request)
        except Exception as e:
            raise e

    @app.on_event("startup")
    async def on_startup_setup():
        # Infrastructure setup
        adapters.views.schemes.update_forward_refs()
        adapters.engines.Database.init()
        await infrastructure.web_framework.routes.init(app)

    @app.on_event("shutdown")
    async def on_shutdown_cleanup():
        # Sessions cleanup
        await adapters.clients.Httpx.close_all()

    return app
