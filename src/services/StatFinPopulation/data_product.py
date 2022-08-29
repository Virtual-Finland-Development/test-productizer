from pydantic import Field
from datetime import datetime
from src.utils.models import DataspaceableModel

#
# Data product models
# @see: https://github.com/Virtual-Finland/definitions/blob/main/src/test/lsipii/Figure/Population.py
#
class PopulationDataProductRequest(DataspaceableModel):
    """
    The data product input syntax
    """

    city: str = Field(
        "",
        title="City or region",
        description="City or a region name, leaving the field empty selects country's total",
    )
    year: int = Field(2021, title="Year")


class PopulationDataProductResponse(DataspaceableModel):
    """
    The data product output syntax
    """

    description: str = Field(
        "", title="Data description", example="Väkiluku, KOKO MAA, 2021"
    )
    source_name: str = Field("", title="Data source name", example="Tilastokeskus")
    population: int = Field(..., title="The population value", example=5548241)
    updated_at: datetime = Field(
        "",
        title="Datetime the data was last updated at. A datetime in RFC3339 date-time syntax",
        example="2022-06-17T11:52:00Z",
    )
