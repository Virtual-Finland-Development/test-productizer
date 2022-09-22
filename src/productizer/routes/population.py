from typing import Union
from fastapi import APIRouter, Header
from productizer.services.StatFinPopulation.models.data_product import (
    PopulationDataProductRequest,
    PopulationDataProductResponse,
)
from productizer.services.StatFinPopulation.service import get_population
from productizer.utils import Authorizator

router = APIRouter()


@router.post(
    "/test/lsipii/Figure/Population",
    summary="test/lsipii/Figure/Population Data Product",
    description="A test Data Product for the population query",
    response_model=PopulationDataProductResponse,
)
async def population(
    request: PopulationDataProductRequest,
    Authorization: Union[str, None] = Header(default=None),
):
    await Authorizator.authorize(Authorization)  # raises 401 if not authorized
    return await get_population(request)
