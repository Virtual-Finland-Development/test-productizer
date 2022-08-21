from typing import Dict, Any, Literal, Type, TypeVar, Generic, TypedDict, Optional, Union, Callable
from pydantic import ValidationError
import orjson
import aiohttp

T = TypeVar("T")

KnownRequestMethods = Literal["GET", "POST"]
RequestParams = Dict[str, Any]
RequestData = Any
RequestHeaders = Dict[str, Any]


class RequestRequiredParts(TypedDict, total=True):
    url: str


class Request(RequestRequiredParts, total=False):
    method: Optional[KnownRequestMethods]
    params: Optional[RequestParams]
    data: Optional[RequestData]
    headers: Optional[RequestHeaders]


async def fetch(
    request: Request,
    response_type: Type[T],
    name: str = "Data fetcher",
    validator: Optional[Callable[[Any], Any]] = None,
) -> T:
    """A wrapper for requester"""
    requester = Requester[response_type](name, request, validator)
    items = await requester.fetch()
    return items  # type: ignore


class Requester(Generic[T]):
    """
    A type-aware wrapper for the aiohttp.ClientSession class"""

    requester_name: str
    request_input: Optional[Request]
    validator: Optional[Callable[[Any], Any]] = None

    def __init__(self, name: str, request: Optional[Request], validator: Optional[Callable[[Any], Any]] = None) -> None:
        self.requester_name = name
        self.request_input = request
        self.validator = validator

    #
    # Requesting methods
    #
    async def fetch(self, request: Optional[Request] = None) -> T:
        if request is not None:
            return await self.request(request)
        return await self.request(self.request_input)

    async def post(
        self,
        url: str,
        params: Optional[RequestParams] = None,
        data: Optional[RequestData] = None,
        headers: Optional[RequestHeaders] = None,
    ) -> T:
        return await self.request(
            {
                "method": "POST",
                "url": url,
                "params": params,
                "data": data,
                "headers": headers,
            }
        )

    async def get(
        self, url: str, params: Optional[RequestParams] = None, headers: Optional[RequestHeaders] = None
    ) -> T:
        return await self.request(
            {
                "method": "GET",
                "url": url,
                "params": params,
                "headers": headers,
            }
        )

    async def request(
        self,
        request: Optional[Request] = None,
    ) -> T:
        if request is None:
            raise Exception("Request input not defined")
        return await self.fetchJSON(**request)

    #
    # Request actuator
    #
    async def fetchJSON(
        self,
        url: str,
        method: Optional[KnownRequestMethods] = None,
        params: Optional[RequestParams] = None,
        data: Optional[RequestData] = None,
        headers: Optional[RequestHeaders] = None,
    ) -> T:
        async with aiohttp.ClientSession() as session:
            opts = {
                "params": params,
                "data": data,
                "headers": headers,
                "skip_auto_headers": ["user-agent"],
                "allow_redirects": False,
                "compress": True,
                "timeout": 30.0,
            }

            request_method = method if method is not None else "GET"

            async with session.request(request_method, url, **opts) as res:
                async with res:
                    if res.status == 200:
                        try:
                            result = await res.json(loads=orjson.loads)
                            self.validate_result(result)
                            return result
                        except Exception as e:
                            raise self.prepare_expection(e)
                    else:
                        text = await res.text()
                        raise self.prepare_expection(text)

    #
    # Utils
    #
    def prepare_expection(self, exception: Union[Exception, str]) -> Exception:
        """Prefix expections with requester name"""
        errorMessagePrefix = f"{self.requester_name}: Error --> "
        if isinstance(exception, aiohttp.ClientResponseError):
            return Exception(f"{errorMessagePrefix}{exception.message}")
        if isinstance(exception, ValidationError):
            return ValueError(f"{errorMessagePrefix}ValidationError --> {exception}")
        return ValueError(f"{errorMessagePrefix}{exception}")

    def validate_result(self, result: T) -> None:
        """Validate result if validator is defined"""
        if callable(self.validator):
            if isinstance(result, list):
                for item in result:  # type: ignore
                    self.validator(item)
            else:
                self.validator(result)
