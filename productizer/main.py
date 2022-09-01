import os
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from mangum import Mangum

from productizer.utils.Requester import BaseRequesterException

from .routes import base, population

#
# FastAPI app definition
#

# Lambda stage path prefix setup
stage = os.environ.get("STAGE", None)
openapi_prefix = f"/{stage}" if stage and stage != "production" else "/"

app = FastAPI(
    title="Test productizer",
    root_path=openapi_prefix,
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#
# Routes
#
app.include_router(base.router)
app.include_router(population.router)

#
# Requester: data source's fetch-exception handlers
#
# @see: https://fastapi.tiangolo.com/tutorial/handling-errors/
#
@app.exception_handler(BaseRequesterException)  # type: ignore
async def requester_exception_handler(
    request: FastAPIRequest, exception: BaseRequesterException
):
    return ORJSONResponse(
        status_code=exception.status_code or exception.default_status_code,
        content={"detail": str(exception)},
    )


#
# serverless function handler
#
handler = Mangum(app)
