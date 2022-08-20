from fastapi import FastAPI
from .services.StatFinResources import get_resources_list

app = FastAPI()

@app.get("/")
@app.get("/resources")
async def resources():
    return await get_resources_list()
