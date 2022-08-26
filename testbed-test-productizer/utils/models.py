from pydantic import BaseModel
from stringcase import camelcase  # type: ignore
from datetime import datetime
from .helpers import convert_datetime_to_iso_8601_with_z_suffix


class DataspaceableModel(BaseModel):
    """
    A pydantic model configuration similar to the data product definitions of the testbed/dataspace api-gw
    @see: https://github.com/ioxiocom/sandbox-definitions/blob/master/src/converter.py

    Also fixes the python datetime timezone serialization from "+000" syntax to the "zulu" syntax as it's referenced in the OpenAPI Specification v3.0.3, RFC3339: date-time
    @see: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#data-types
    @see: https://www.rfc-editor.org/rfc/rfc3339#section-5.6
    @see: https://stackoverflow.com/a/68198142
    """

    class Config:
        alias_generator = camelcase  # type: ignore
        allow_population_by_field_name = True
        json_encoders = {
            # custom output conversion for datetime
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }
