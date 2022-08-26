from pydantic import BaseModel, Field
from datetime import datetime

#
# Data models
#
class StatFinPopulationDataProductInput(BaseModel):
    """
    The data product input syntax
    """

    city: str = Field(
        "",
        title="City or region",
        description="City or a region name, leaving the field empty selects country's total",
    )
    year: int = Field(2021, title="Year")


class StatFinPopulationDataProduct(BaseModel):
    """
    The data product output syntax
    """

    description: str = Field("", title="Data description")
    source_name: str = Field("", title="Data source name")
    population: int = Field(..., title="The population value")
    updated_at: datetime = Field("", title="Data updated at datetime")
