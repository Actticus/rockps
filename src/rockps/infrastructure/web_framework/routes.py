import fastapi

from rockps.adapters import views


async def init(app: fastapi.FastAPI):
    # TODO: Fix after migration on class-based views

    # pylint: disable=line-too-long
    _ROUTER_CONFIGS = [
    ]

    for router_config in _ROUTER_CONFIGS:
        app.include_router(**router_config)
