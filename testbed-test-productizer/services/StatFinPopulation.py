from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel
from ..utils.Requester import fetch

"""
The data source endpoint URL
"""
get_api_endpoint: Callable[
    [str], str
] = (
    lambda locale: f"https://statfin.stat.fi/PXWeb/api/v1/{locale}/Kuntien_avainluvut/2021/kuntien_avainluvut_2021_aikasarja.px"
)

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


class StatFinFiguresResponseVariables(BaseModel):
    code: str
    text: str
    values: List[str]
    valueTexts: List[str]


class StatFinFiguresResponse(BaseModel):
    title: str
    variables: List[StatFinFiguresResponseVariables]


class StatFinPopulationDataProductInput(BaseModel):
    """
    The data product input syntax
    """

    city_query: Optional[str] = ""
    year: Optional[int] = 2021


#
# Output item model(s)
#
class StatFinPopulationDataProduct(BaseModel):
    """
    The data product output syntax
    """

    label: str
    source: str
    value: int
    updated: str


#
# The request handler
#
async def get_population(city_query: str = "", year: int = 2021, locale: str = "fi") -> StatFinPopulationDataProduct:
    """
    The getter function for the resources list
    """

    resource_url = get_api_endpoint(locale)
    API_code_for_area = await resolve_api_code_for_area(city_query, year, locale)
    API_code_for_population_search = "M411"

    # Fetch items from the external data source API
    item = await fetch(
        name=__name__,
        request={
            "method": "POST",
            "url": resource_url,
            "data": {
                "query": [
                    {
                        "code": f"Alue 2021",
                        "selection": {"filter": "item", "values": [API_code_for_area]},
                    },
                    {
                        "code": "Tiedot",
                        "selection": {"filter": "item", "values": [API_code_for_population_search]},
                    },
                    {"code": "Vuosi", "selection": {"filter": "item", "values": [year]}},
                ],
                "response": {"format": "json-stat2"},
            },
        },
        response_type=StatFinPopulationResponse,  # for type hinting
        formatter=StatFinPopulationResponse.parse_obj,  # also validates the response
    )

    # Transform and return response items to data product syntax
    return StatFinPopulationDataProduct(
        label=format_data_product_label(item, year), source=item.source, value=item.value[0], updated=item.updated
    )


async def resolve_api_code_for_area(city_query: str, year: int, locale: str) -> str:
    """
    Resolves the API code for the area
    """

    API_code_for_area = "SSS"  # Defaut: all areas
    if len(city_query) > 0:
        search_phrase = city_query.lower().strip()
        resource_url = get_api_endpoint(locale)

        figures = await fetch(
            {"url": resource_url},
            response_type=StatFinFiguresResponse,
            formatter=StatFinFiguresResponse.parse_obj,  # validates the response
        )

        figure_variables = list(figures.variables)[0]
        if len(figure_variables.values) != len(figure_variables.valueTexts):
            raise ValueError("Invalid city fiqures received")

        city_names = figure_variables.valueTexts
        city_name = next(filter(lambda city_name: city_name.lower() == search_phrase, city_names), None)
        if city_name is not None:
            index = city_names.index(city_name)
            API_code_for_area = figure_variables.values[index]
        else:
            error_message = f"City '{city_query}' not found"

            suggestions = list(filter(lambda city_name: city_name.lower().__contains__(search_phrase), city_names))
            if len(suggestions) > 0:
                error_message = f"{error_message}, try one of {suggestions}"

            raise ValueError(error_message)

    return API_code_for_area


def format_data_product_label(item: StatFinPopulationResponse, year: int) -> str:
    """
    Formats the data product label
    """
    dimensions = list(item.dimension.values())
    first_dimension_category_label = list(dimensions[0].category.label.values())[0]
    second_dimension_label = list(dimensions[1].category.label.values())[0]
    return f"{second_dimension_label}, {first_dimension_category_label}, {year}"
