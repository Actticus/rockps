import fastapi

from rockps.adapters import views


async def init(app: fastapi.FastAPI):
    # TODO: Fix after migration on class-based views

    # pylint: disable=line-too-long
    _ROUTER_CONFIGS = [
        {"router": views.v1.auth.SignUp().router, "prefix": "/v1/auth/signup"},
        {"router": views.v1.auth.SignIn().router, "prefix": "/v1/auth/signin"},
    ]

    for router_config in _ROUTER_CONFIGS:
        app.include_router(**router_config)
