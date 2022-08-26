from fastapi import APIRouter, HTTPException

router = APIRouter()

from ..services.StatFinPopulation import PopulationDataProductResponse, PopulationDataProductRequest, get_population
from pydantic import ValidationError


@router.post(
    "/test/Figure/Population",
    summary="test/Figure/Population Data Product",
    description="A test Data Product for the population query",
    response_model=PopulationDataProductResponse,
)
async def population(
    request: PopulationDataProductRequest,
):
    try:
        return await get_population(request)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
