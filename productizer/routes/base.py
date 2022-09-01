from fastapi import APIRouter
from fastapi.responses import RedirectResponse, PlainTextResponse

router = APIRouter()

#
# Base routes
#
@router.get(
    "/",
    summary="redirect to /docs",
    description="A redirect to /docs",
)
async def root():
    return RedirectResponse("/docs")


@router.get(
    "/health",
    summary="A health check",
    description="Should response with 200 OK",
)
async def healthCheck():
    return PlainTextResponse("OK", status_code=200)
