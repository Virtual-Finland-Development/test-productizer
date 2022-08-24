from fastapi import APIRouter
from ..services.SAML_SuomiFi import get_suomi_fi_saml_client
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/saml/login", summary="A login page", description="An auth redirect to the identity provider (AuthNRequest)"
)
async def auth_n_request():
    client = await get_suomi_fi_saml_client()
    session_id, auth_n_request_info = client.prepare_for_authenticate()  # type: ignore
    redirect_url: str = auth_n_request_info["headers"][0][1]  # type: ignore
    return RedirectResponse(redirect_url, status_code=303)


@router.get("/saml/logout", summary="A logout page", description="")
async def logout():
    raise Exception("Not implemented")
