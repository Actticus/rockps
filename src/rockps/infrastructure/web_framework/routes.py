import fastapi

from rockps.adapters import views


async def init(app: fastapi.FastAPI):
    # TODO: Fix after migration on class-based views

    # pylint: disable=line-too-long
    _ROUTER_CONFIGS = [
        {"router": views.v1.auth.SignUp().router, "prefix": "/api/v1/auth/signup"},
        {"router": views.v1.auth.SignIn().router, "prefix": "/api/v1/auth/signin"},
        {"router": views.v1.auth.Confirm().router, "prefix": "/api/v1/auth/confirm"},
        {"router": views.v1.auth.resetpass.ResetPassRequest().router, "prefix": "/api/v1/auth/reset-password/request"},
        {"router": views.v1.auth.resetpass.ResetPasswordCertify().router, "prefix": "/api/v1/auth/reset-password/certify"},
        {"router": views.v1.auth.resetpass.ResetPasswordNew().router, "prefix": "/api/v1/auth/reset-password/new"},

        {"router": views.v1.lobby.Lobby().router, "prefix": "/api/v1/lobby"},
    ]

    for router_config in _ROUTER_CONFIGS:
        app.include_router(**router_config)
