from fastapi import APIRouter
from productizer.services.StatFinPopulation import (
    PopulationDataProductResponse,
    PopulationDataProductRequest,
    get_population,
)

router = APIRouter()


@router.post(
    "/test/lsipii/Figure/Population",
    summary="test/lsipii/Figure/Population Data Product",
    description="A test Data Product for the population query",
    response_model=PopulationDataProductResponse,
)
async def population(
    request: PopulationDataProductRequest,
):
    return await get_population(request)
