from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/",
    summary="redirect to /docs",
    description="A redirect to /docs",
)
async def root():
    return RedirectResponse("/docs")
