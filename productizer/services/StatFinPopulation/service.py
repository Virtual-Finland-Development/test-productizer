from datetime import datetime
from typing import Callable
from productizer.utils.Requester import RequesterResponseParsingException, fetch
from productizer.services.StatFinPopulation.data_source_api_models import (
    StatFinFiguresResponse,
    StatFinPopulationResponse,
)
from productizer.services.StatFinPopulation.data_product import (
    PopulationDataProductResponse,
    PopulationDataProductRequest,
)
from dateutil import parser as date_parser

"""
The data source endpoint URL
"""
get_api_endpoint: Callable[
    [str], str
] = (
    lambda locale: f"https://statfin.stat.fi/PXWeb/api/v1/{locale}/Kuntien_avainluvut/2021/kuntien_avainluvut_2021_aikasarja.px"
)

#
# The request handler
#
async def get_population(
    request: PopulationDataProductRequest,
) -> PopulationDataProductResponse:
    """
    The getter function for the resources list
    """
    city = request.city if request.city is not None else ""
    year = request.year if request.year is not None else 2021
    locale = "fi"

    resource_url = get_api_endpoint(locale)
    API_code_for_area = await resolve_api_code_for_area(city, locale)
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
                        "selection": {
                            "filter": "item",
                            "values": [API_code_for_population_search],
                        },
                    },
                    {
                        "code": "Vuosi",
                        "selection": {"filter": "item", "values": [year]},
                    },
                ],
                "response": {"format": "json-stat2"},
            },
        },
        formatter=StatFinPopulationResponse,  # ensure correct pydantic output
    )

    # Transform and return response items to data product syntax
    return PopulationDataProductResponse(
        description=format_data_product_description(item, year),
        source_name=item.source,
        population=item.value[0],
        updated_at=format_data_product_updated_at(item.updated),
    )


async def resolve_api_code_for_area(city: str, locale: str) -> str:
    """
    Resolves the API code for the area
    """

    API_code_for_area = "SSS"  # Defaut: all areas
    if len(city) > 0:
        search_phrase = city.lower().strip()
        resource_url = get_api_endpoint(locale)

        # Fetch figures for city code resolving
        figures = await fetch(
            request={"url": resource_url}, formatter=StatFinFiguresResponse
        )

        # Resolve city code
        figure_variables = list(figures.variables)[0]
        if len(figure_variables.values) != len(figure_variables.valueTexts):
            raise RequesterResponseParsingException(
                message="Invalid city fiqures received"
            )

        city_names = figure_variables.valueTexts
        city_name = next(
            filter(lambda city_name: city_name.lower() == search_phrase, city_names),
            None,
        )
        if city_name is not None:
            index = city_names.index(city_name)
            API_code_for_area = figure_variables.values[index]
        else:
            error_message = f"City '{city}' not found"

            suggestions = list(
                filter(
                    lambda city_name: city_name.lower().__contains__(search_phrase),
                    city_names,
                )
            )
            if len(suggestions) > 0:
                error_message = f"{error_message}, try one of {suggestions}"

            raise RequesterResponseParsingException(message=error_message)

    return API_code_for_area


#
# Formatters
#


def format_data_product_description(item: StatFinPopulationResponse, year: int) -> str:
    """
    Formats the data product label
    """
    dimensions = list(item.dimension.values())
    first_dimension_category_label = list(dimensions[0].category.label.values())[0]
    second_dimension_label = list(dimensions[1].category.label.values())[0]
    return f"{second_dimension_label}, {first_dimension_category_label}, {year}"


def format_data_product_updated_at(updated: str) -> datetime:
    """
    2022-06-17T11.52.00Z -> 2022-06-17T11:52:00Z -> datetime
    """
    corrected_syntax = updated.replace(".", ":") if updated.count(".") == 2 else updated
    return date_parser.parse(corrected_syntax)
