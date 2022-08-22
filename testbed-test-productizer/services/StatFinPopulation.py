from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..utils.Requester import fetch
from ..data.city_codes import CITY_CODES

configuration = {
    "API_ENDPOINT": "https://statfin.stat.fi/PXWeb/api/v1",
    "API_CODE_FOR_POPULATION_SEARCH": "M411",
}

#
# External API response item model(s)
#
class StatFinPopulationResponseDimensionsCategory(BaseModel):
    index: Dict[str, str]
    label: Dict[str, str]
    unit: Optional[Dict[str, Dict[str, Any]]]


class StatFinPopulationResponseDimensions(BaseModel):
    label: str
    category: StatFinPopulationResponseDimensionsCategory


class StatFinPopulationResponse(BaseModel):
    """
    The expected structure of the data sources item in the external API response
    --> The data source syntax"""

    label: str
    source: str
    updated: str
    dimension: Dict[str, StatFinPopulationResponseDimensions]
    id: List[str]
    size: List[int]
    value: List[int]  # the result should be in value[0]
    version: str


#
# Output item model(s)
#
class StatFinPopulationDataProduct(BaseModel):
    """
    The syntax for the output item
    --> The data product syntax"""

    label: str
    source: str
    value: int
    updated: str


#
# The request handler
#
async def get_population(city_query: str = "", year: str = "2021", locale: str = "fi") -> StatFinPopulationDataProduct:
    """
    The getter function for the resources list
    """

    resource_url_path = f"{locale}/Kuntien_avainluvut/{year}/kuntien_avainluvut_{year}_viimeisin.px"  # @note: the path is correct for all locales
    resource_url = f"{configuration['API_ENDPOINT']}/{resource_url_path}"
    API_code_for_area = resolve_api_code_for_area(city_query)

    # Fetch items from the external data source API
    item = await fetch(
        name=__name__,
        request={
            "method": "POST",
            "url": resource_url,
            "data": {
                "query": [
                    {
                        "code": f"Alue {year}",
                        "selection": {"filter": "item", "values": [API_code_for_area]},
                    },
                    {
                        "code": "Tiedot",
                        "selection": {"filter": "item", "values": [configuration["API_CODE_FOR_POPULATION_SEARCH"]]},
                    },
                ],
                "response": {"format": "json-stat2"},
            },
        },
        response_type=StatFinPopulationResponse,  # for type hinting
        formatter=StatFinPopulationResponse.parse_obj,  # also validates the response
    )

    # Transform and return response items to data product syntax
    return StatFinPopulationDataProduct(label=item.label, source=item.source, value=item.value[0], updated=item.updated)


def resolve_api_code_for_area(city_query: str) -> str:
    """
    Resolves the API code for the area
    """

    API_code_for_area = "SSS"  # Defaut: all areas
    if len(city_query) > 0:
        search_phrase = city_query.lower().strip()
        region_entity = next(filter(lambda region: region["name"].lower() == search_phrase, CITY_CODES), None)
        if region_entity is None:
            suggestions = list(
                map(
                    lambda i: i["name"],
                    filter(lambda region: region["name"].lower().__contains__(search_phrase), CITY_CODES),
                )
            )
            raise ValueError(f"City {city_query} not found: try one of {suggestions}")
        API_code_for_area = region_entity["code"]

    return API_code_for_area
