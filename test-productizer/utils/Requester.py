from typing import Dict, Any, Literal, TypeVar, Generic, TypedDict, Optional, Union
import orjson
import aiohttp

T = TypeVar("T")

KnownRequestMethods = Literal["GET", "POST"]
RequestParams = Dict[str, Any]
RequestData = Any


class BaseRequest(TypedDict, total=True):
    url: str


class Request(BaseRequest, total=False):
    method: Optional[KnownRequestMethods]
    params: Optional[RequestParams]
    data: Optional[RequestData]
    headers: Optional[Dict[str, Any]]


"""
A type-awareish wrapper for the aiohttp.ClientSession class
"""


async def fetch(name: str, response_type: T, request: Optional[Request]) -> T:
    requester = Requester[T](name, request)
    return await requester.fetch()


# Implementation of the Requester
class Requester(Generic[T]):
    requester_name: str
    request_input: Optional[Request]

    def __init__(self, name: str, request: Optional[Request]) -> None:
        self.requester_name = name
        self.request_input = request

    """
    Requesting methods
    """

    async def fetch(self) -> T:
        if self.request_input is not None:
            return await self.request(
                self.request_input["method"] if "method" in self.request_input else None,
                self.request_input["url"],
                self.request_input["params"] if "params" in self.request_input else None,
                self.request_input["data"] if "data" in self.request_input else None,
            )
        else:
            raise Exception("Request input not defined")

    async def request(
        self,
        method: Optional[KnownRequestMethods],
        url: str,
        params: Optional[RequestParams] = None,
        data: Optional[RequestData] = None,
    ) -> T:
        return await self.fetchJSON(method, url, params, data)

    async def post(self, url: str, params: Optional[RequestParams] = None, data: Optional[RequestData] = None) -> T:
        return await self.request("POST", url, params, data)

    async def get(self, url: str, params: Optional[RequestParams] = None) -> T:
        return await self.request("GET", url, params)

    """
    Request actuator
    """

    async def fetchJSON(
        self,
        method: Optional[KnownRequestMethods],
        url: str,
        params: Optional[RequestParams] = None,
        data: Optional[RequestData] = None,
    ) -> T:
        try:
            async with aiohttp.ClientSession() as session:
                opts = {
                    "params": params,
                    "data": data,
                    "skip_auto_headers": ["user-agent"],
                    "allow_redirects": False,
                    "compress": True,
                    "timeout": 30.0,
                }

                request_method = method if method is not None else "GET"

                async with session.request(request_method, url, **opts) as res:
                    async with res:
                        if res.status == 200:
                            return await res.json(loads=orjson.loads)
                        else:
                            text = await res.text()
                            raise self.prepare_expection(text)
        except Exception as e:
            raise self.prepare_expection(e)

    def prepare_expection(self, exception: Union[Exception, str]) -> Exception:
        errorMessagePrefix = f"{self.requester_name}: Error --> "
        if isinstance(exception, aiohttp.ClientResponseError):
            return Exception(f"{errorMessagePrefix}{exception.message}")
        return ValueError(f"{errorMessagePrefix}{exception}")
