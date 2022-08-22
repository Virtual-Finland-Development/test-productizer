from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from .services.StatFinPopulation import StatFinPopulationDataProduct, get_population
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
    city_query: str = "",
    year: str = "2021",
):
    try:
        return await get_population(city_query, year)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
