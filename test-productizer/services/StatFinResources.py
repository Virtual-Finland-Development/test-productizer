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
    # Define the external data source API requester
    response_type = List[StatFinResourcesResponseInputListItem]  # typehint for the response
    requester = Requester[response_type](
        name="Get resources list",
        request={
            "url": configuration["API_ENDPOINT"],
            "params": {
                "query": query,
                "filter": filters,
            },
        },
    )

    # Fetch items from the external data source API
    items = await requester.fetch()

    # Transform and return response items to data product syntax
    return list(map(lambda item: StatFinResourcesResponseOutputListItem.parse_obj(item), items))
