from pydantic import BaseModel, Field
from datetime import datetime

#
# Data product models
# @see: https://github.com/Virtual-Finland/definitions/blob/main/src/test/lsipii/Figure/Population.py
#
class PopulationDataProductRequest(BaseModel):
    """
    The data product input syntax
    """

    city: str = Field(
        "",
        title="City or region",
        description="City or a region name, leaving the field empty selects country's total",
    )
    year: int = Field(2021, title="Year")


class PopulationDataProductResponse(BaseModel):
    """
    The data product output syntax
    """

    description: str = Field("", title="Data description")
    source_name: str = Field("", title="Data source name")
    population: int = Field(..., title="The population value")
    updated_at: datetime = Field("", title="Data updated at datetime")
