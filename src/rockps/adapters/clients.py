import weakref

import httpx


class Httpx(httpx.AsyncClient):
    __refs__ = []

    def __init__(self, **kwargs) -> None:
        self.__refs__.append(weakref.ref(self))
        super().__init__(**kwargs)

    @classmethod
    async def close_all(cls):
        for ref in cls.__refs__:
            if (instance := ref()) is not None:
                await instance.aclose()
