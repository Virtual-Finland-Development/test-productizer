from typing import Optional
from pydantic import BaseModel


class StatFinPopulationDataProductInput(BaseModel):
    """
    The data product input syntax
    """

    city: Optional[str] = ""
    year: Optional[int] = 2021


#
# Output item model(s)
#
class StatFinPopulationDataProduct(BaseModel):
    """
    The data product output syntax
    """

    label: str
    source: str
    value: int
    updated: str
