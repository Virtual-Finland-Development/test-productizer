from typing import List
from pydantic import BaseModel
from ..utils.Requester import fetch

configuration = {
    "API_ENDPOINT": "https://statfin.stat.fi/pxweb/api/v1/en/StatFin/",
}


class StatFinResourcesResponseInputListItem(BaseModel):
    """
    The expected structure of the data sources item in the external API response
    --> The data source syntax"""

    published: str
    score: float
    title: str
    path: str
    id: str


class StatFinResourcesResponseOutputListItem(BaseModel):
    """
    The syntax for the output item
    --> The data product syntax"""

    title: str
    path: str
    id: str


async def get_resources_list(query: str = "*", filters: str = "*") -> List[StatFinResourcesResponseOutputListItem]:
    """
    The getter function for the resources list
    """

    # Fetch items from the external data source API
    items = await fetch(
        name=__name__,
        request={
            "url": configuration["API_ENDPOINT"],
            "params": {
                "query": query,
                "filter": filters,
            },
        },
        response_type=List[StatFinResourcesResponseInputListItem],
    )

    # Transform and return response items to data product syntax
    return list(map(lambda item: StatFinResourcesResponseOutputListItem.parse_obj(item), items))
