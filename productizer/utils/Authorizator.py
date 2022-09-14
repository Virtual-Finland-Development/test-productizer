from typing import Union

from productizer.utils.Requester import fetch
from productizer.utils.helpers import base64_encode
from productizer.utils.settings import get_setting, if_test_mode
from urllib.parse import quote


def generate_app_context() -> str:
    """
    Generates a string that is used to identify the application
    """
    return quote(base64_encode({"appName": "Test productizer"}))


async def authorize(authorization_header: Union[str, None]) -> None:
    """
    Throws 401 if not authorized
    """
    if if_test_mode():
        return
    await fetch(
        {
            "url": f"{get_setting('AUTHORIZATION_GW_ENDPOINT_URL')}/auth/openid/authorize",
            "method": "POST",
            "data": {
                "appContext": generate_app_context(),
                "token": authorization_header,
            },
        }
    )
