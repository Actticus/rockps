import hashlib
import json
import time

import httpx

from rockps import settings
from rockps.adapters import clients

_CLIENT = None


def dumps_minimized(obj):
    return json.dumps(obj, separators=(',', ':'))


async def _get_session():
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = clients.Httpx()
    return _CLIENT


def _raise_for_error_responce(func):
    async def wrapper(*args, **kwargs):
        try:
            response_body = await func(*args, **kwargs)
        except httpx.HTTPError as e:
            raise e
        else:
            # TODO: Add logger
            status = response_body.get("status")
            if status != "success" or \
                    response_body["data"]["result"] == "error":
                raise Exception(response_body)
        # TODO: Add async task for reply if error
        return response_body
    return wrapper


def _get_request_signature(endpoint, params):
    timestamp = str(int(time.time()))
    signature_content = [
        endpoint,
        timestamp,
        settings.NEWTEL_API_KEY,
        dumps_minimized(params),
        settings.NEWTEL_SIGNING_KEY,
    ]
    signature_str = "\n".join(signature_content)
    signature = hashlib.sha256(signature_str.encode('utf-8')).hexdigest()
    return f"{settings.NEWTEL_API_KEY}{timestamp}{signature}"


@_raise_for_error_responce
async def _request(endpoint: str, data: dict):
    url = f"https://api.new-tel.net/{endpoint}"
    signature = _get_request_signature(endpoint, data)
    headers = {
        "Authorization": f"Bearer {signature}",
        "Content-Type": "application/json",
    }
    session = await _get_session()
    response = await session.post(
        url=url,
        data=dumps_minimized(data),
        headers=headers,
    )
    return response.json()


async def call(number: str, code: int):
    response_body = await _request(
        endpoint="call-password/start-password-call",
        data={
            "async": 1,
            "dstNumber": number.removeprefix("+"),
            "pin": str(code),
            "timeout": 45,
        },
    )
    call_id = response_body["data"]["callDetails"]["callId"]
    return call_id
