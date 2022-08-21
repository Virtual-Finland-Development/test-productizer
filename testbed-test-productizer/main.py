from fastapi import FastAPI
from .services.StatFinPopulation import StatFinPopulationDataProduct, get_population

app = FastAPI()


@app.get(
    "/",
    summary="redirect to /population",
    description="A redirect to /population",
)
@app.get(
    "/population",
    summary="test/undefied/population Data Product",
    description="A test Data Product for the population query",
    response_model=StatFinPopulationDataProduct,
)
async def population():
    return await get_population()
