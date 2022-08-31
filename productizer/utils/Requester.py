from typing import (
    Dict,
    Any,
    Literal,
    TypeVar,
    Generic,
    TypedDict,
    Optional,
    Union,
    Callable,
    Type,
)
import orjson
import aiohttp
from productizer.utils.helpers import (
    ensure_json_content_type_header,
    omit_empty_dict_attributes,
)

#
# Interfaces & types
#
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
    json: Optional[bool]  # = True


#
# Exceptions
#


class BaseRequesterException(Exception):
    name: str
    exception: Optional[Exception]
    message: Optional[str]
    status_code: Optional[int]
    default_status_code: int = 500

    def __init__(
        self,
        name: str,
        exception: Optional[Exception] = None,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.name = name
        self.exception = exception
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        prefix = f"Requester -> {self.name} -> "
        if self.exception is None:
            message = self.message or "Error"
            if self.status_code is not None:
                message = f"{message}: {self.status_code}"
            return f"{prefix}{message}"
        return f"{prefix}{self.exception}"


class RequesterResponseParsingException(BaseRequesterException):
    default_status_code = 422
    pass


class RequesterResponseException(BaseRequesterException):
    pass


#
# Callables, implementations
#


async def fetch(
    request: Request,
    name: str = "Data fetcher",
    formatter: Optional[Union[Callable[[Any], T], Type[T]]] = None,
) -> T:
    """
    A type-keen data fetcher

    @examples:
    response: Any = await fetch(
        {"url": resource_url"},
    )

    response = await fetch(
        {"url": resource_url", "method": "POST", "data": {"id": "abc123"}},
        formatter: PydanticBaseModel
    )
    """
    requester = Requester[T](name, request, formatter)
    items = await requester.fetch()
    return items


class Requester(Generic[T]):
    """
    A type-aware wrapper for the aiohttp.ClientSession class"""

    requester_name: str
    request_input: Optional[Request]
    formatter: Optional[Union[Callable[[Any], T], Type[T]]] = None

    def __init__(
        self,
        name: str,
        request: Optional[Request],
        formatter: Optional[Union[Callable[[Any], T], Type[T]]] = None,
    ) -> None:
        self.requester_name = name
        self.request_input = request
        self.formatter = formatter

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
        self,
        url: str,
        params: Optional[RequestParams] = None,
        headers: Optional[RequestHeaders] = None,
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
        return await self.exec_fetch(**request)

    #
    # Utils
    #
    def format_result(self, result: Any) -> T:
        """Validate & format result if formatter is defined"""
        if callable(self.formatter):
            return self.formatter(**result)  # type: ignore
        return result

    #
    # Request actuator
    #
    async def exec_fetch(
        self,
        url: str,
        method: Optional[KnownRequestMethods] = None,
        params: Optional[RequestParams] = None,
        data: Optional[RequestData] = None,
        headers: Optional[RequestHeaders] = None,
        json: Optional[bool] = None,
    ) -> T:
        # https://github.com/aio-libs/aiohttp/issues/5975
        orjson_wrapped: Callable[[Any], str] = lambda i: (orjson.dumps(i).decode())

        # Prep opts
        if json is None:
            json = True

        opts = {
            "params": params,
            "skip_auto_headers": ["user-agent"],
            "allow_redirects": False,
            # "compress": True,
            "timeout": 30.0,
        }
        if json:
            opts["json"] = data
            opts["headers"] = ensure_json_content_type_header(headers)
        else:
            opts["body"] = data
            opts["headers"] = headers

        options = omit_empty_dict_attributes(opts)

        request_method = method.upper() if method is not None else "GET"

        async with aiohttp.ClientSession(json_serialize=orjson_wrapped) as session:
            async with session.request(request_method, url, **options) as res:
                async with res:
                    if res.status == 200:
                        try:
                            if json:
                                result = await res.json(loads=orjson.loads)
                                return self.format_result(
                                    result
                                )  # throws validation errors that must be handled in the upper abstraction
                            return await res.text()  # type: ignore
                        except Exception as e:
                            raise RequesterResponseParsingException(
                                name=self.requester_name, exception=e
                            )
                    else:
                        message = await res.text()
                        raise RequesterResponseException(
                            name=self.requester_name,
                            message=message,
                            status_code=res.status,
                        )
