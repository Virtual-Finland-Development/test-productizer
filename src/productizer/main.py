from logging import getLogger

from fastapi import FastAPI
from fastapi import Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from mangum import Mangum

from productizer.utils.logger import LoggingMiddleware
from productizer.utils.Requester import BaseRequesterException

from .routes import base, population

#
# FastAPI app definition
#
app = FastAPI(
    title="Test productizer",
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
# Logging
#
logger = getLogger(__name__)
app.add_middleware(LoggingMiddleware, logger=logger)

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
    status_code = exception.status_code or exception.default_status_code
    content = {"detail": str(exception)}
    logger.warning("Exception status code: %d, content: %s", status_code, content)

    return ORJSONResponse(
        status_code=status_code,
        content=content,
    )


#
# serverless function handler
#
handler = Mangum(app)
