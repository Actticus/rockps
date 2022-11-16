import abc


class ClickhouseClient:

    @classmethod
    @abc.abstractmethod
    async def post(cls, *args, **kwargs):
        pass

    @classmethod
    @abc.abstractmethod
    async def get(cls, *args, **kwargs):
        pass
