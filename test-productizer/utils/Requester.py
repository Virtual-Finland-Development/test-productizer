from typing import Dict, Any, Literal, TypeVar, Generic
import orjson
import aiohttp
T = TypeVar('T')


"""
A type-aware wrapper for the aiohttp.ClientSession class
"""
def Requester(name: str, response_type: Any):
    return ___Requester[response_type](name)

class ___Requester(Generic[T]):
    requester_name: str
    def __init__(self, requester_name: str) -> None:
        self.requester_name = requester_name

    async def post(self,  url: str = "", params: Dict[str, Any] = None, data: Any = None) -> T:
        return await self.fetchJSON("POST", url, params, data)
    async def get(self,  url: str = "", params: Dict[str, Any] = None) -> T:
        return await self.fetchJSON("GET", url, params)


    async def fetchJSON(self, method: Literal["GET", "POST"], url: str, params: Dict[str, Any] = None, data: Any = None) -> T:
        try:
            async with aiohttp.ClientSession() as session:
                opts = {
                    "params":params,
                    "data":data,
                    "skip_auto_headers": ["user-agent"],
                    "allow_redirects": False,
                    "compress": True,
                    "timeout": 30.0,
                }

                async with session.request(method.upper(), url, **opts) as res:
                    async with res:
                        if res.status == 200:
                            return await res.json(loads=orjson.loads)
                        else:
                            text = await res.text()
                            return self.error_handler(text)
        except Exception as e:
            return self.error_handler(e)

    
    def error_handler(self, exception) -> None:
        errorMessagePrefix = f"{self.requester_name}: Error --> "
        if isinstance(exception, aiohttp.ClientResponseError):
            raise Exception(f"{errorMessagePrefix}{exception.message}")
        raise ValueError(f"{errorMessagePrefix}{exception}")