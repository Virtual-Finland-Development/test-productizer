from fastapi import FastAPI, HTTPException
from .services.StatFinPopulation import StatFinPopulationDataProduct, get_population

app = FastAPI()


@app.get(
    "/",
    summary="redirect to /test/undefied/population",
    description="A redirect to /test/undefied/population",
)
@app.get(
    "/test/undefied/population",
    summary="test/undefied/population Data Product",
    description="A test Data Product for the population query",
    response_model=StatFinPopulationDataProduct,
)
async def population(
    city_query: str = "",
    year: str = "2021",
):
    try:
        return await get_population(city_query, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
