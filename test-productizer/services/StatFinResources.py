from typing import List
from pydantic import BaseModel
from ..utils.Requester import Requester

configuration = {
    "API_ENDPOINT": "https://statfin.stat.fi/pxweb/api/v1/en/StatFin/",
}

"""
The expected structure of the data sources singular item in the external API request response (input)
"""
class StatFinResourcesResponseInputListItem(BaseModel):
    published: str
    score: float
    title: str
    path: str
    id: str

"""
The syntax for the output item
--> The data product syntax
"""
class StatFinResourcesResponseOutputListItem(BaseModel):
    title: str
    path: str
    id: str


"""
The getter function for the resources list
"""
async def get_resources_list(query: str = "*", filters: str = "*") -> List[StatFinResourcesResponseOutputListItem]:
    requester = Requester(name="Get resources list", response_type=List[StatFinResourcesResponseInputListItem])
    request = {
        "url": configuration["API_ENDPOINT"], 
        "params": {
            "query": query,
            "filter": filters,
        }
    }

    items = await requester.get(**request)

    return list(map(lambda item: StatFinResourcesResponseOutputListItem(**item), items))