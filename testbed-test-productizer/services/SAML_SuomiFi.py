from saml2.client import Saml2Client  # type: ignore
from saml2.config import Config as Saml2Config  # type: ignore

from ..utils.Requester import fetch


async def fetch_suomi_fi_metadata():
    return await fetch(
        {"url": "https://tunnistus.suomi.fi/static/metadata/idp-metadata-tunnistautuminen.xml", "json": False}
    )


async def metadata_def():
    return """
    
    """


# @see: https://pysaml2.readthedocs.io/en/latest/howto/config.html
async def get_suomi_fi_saml_client():

    metadata = await metadata_def()
    settings = {
        "metadata": {
            "inline": [metadata],
        },
        "encryption_keypairs": [
            {
                "key_file": "data/certificates/private.key",
                "cert_file": "data/certificates/public.cert",
            },
        ],
        "service": {
            "sp": {
                "endpoints": {
                    "assertion_consumer_service": [
                        (
                            "https://kalastus.mallikunta.fi/SAML/ACS/POST",
                            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                        ),
                    ],
                }
            },
        },
    }
    spConfig = Saml2Config()
    spConfig.load(settings)  # type: ignore
    spConfig.allow_unknown_attributes = True  # type: ignore
    saml_client = Saml2Client(config=spConfig)
    return saml_client
