from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, ORJSONResponse

from .services.StatFinPopulation import StatFinPopulationDataProduct, StatFinPopulationDataProductInput, get_population
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    summary="redirect to /docs",
    description="A redirect to /docs",
)
async def root():
    return RedirectResponse("/docs")


@app.post(
    "/test/undefined/population",
    summary="test/undefined/population Data Product",
    description="A test Data Product for the population query",
    response_model=StatFinPopulationDataProduct,
)
async def population(
    city_query: Optional[str] = None,
    year: Optional[int] = None,
    request: Optional[StatFinPopulationDataProductInput] = None,
):
    try:

        #
        # Merge request query params and body
        #
        params = {
            "city_query": city_query,
            "year": year,
        }
        if request is not None:
            request_fields = request.dict()
            for entry in params.keys():
                if entry in request_fields and bool(request_fields[entry]):
                    params[entry] = request_fields[entry]

        return await get_population(**params)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
