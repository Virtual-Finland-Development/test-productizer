from fastapi import APIRouter, HTTPException

router = APIRouter()

from ..services.StatFinPopulation import StatFinPopulationDataProduct, StatFinPopulationDataProductInput, get_population
from pydantic import ValidationError
from typing import Optional


@router.post(
    "/test/Figure/Population",
    summary="test/Figure/Population Data Product",
    description="A test Data Product for the population query",
    response_model=StatFinPopulationDataProduct,
)
async def population(
    city: Optional[str] = None,
    year: Optional[int] = None,
    request: Optional[StatFinPopulationDataProductInput] = None,
):
    try:

        #
        # Merge request query params and body
        #
        params = {
            "city": city,
            "year": year,
        }
        if request is not None:
            request_fields = request.dict()
            for entry in params.keys():
                if entry in request_fields and bool(request_fields[entry]):
                    params[entry] = request_fields[entry]

        return await get_population(StatFinPopulationDataProductInput.parse_obj(params))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
