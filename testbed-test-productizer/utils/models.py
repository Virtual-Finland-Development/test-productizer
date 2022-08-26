from pydantic import BaseModel
from stringcase import camelcase  # type: ignore


class CamelCaseModel(BaseModel):
    """
    A pydantic model configuration similar to the data product definitions of the testbed/dataspace api-gw
    @see: https://github.com/ioxiocom/sandbox-definitions/blob/master/src/converter.py
    """

    class Config:
        alias_generator = camelcase  # type: ignore
        allow_population_by_field_name = True
