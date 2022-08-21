from fastapi import FastAPI
from .services.StatFinPopulation import get_population

app = FastAPI()


@app.get("/")
@app.get("/population")
async def population():
    return await get_population()
