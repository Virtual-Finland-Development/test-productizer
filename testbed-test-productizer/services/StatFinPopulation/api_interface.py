from typing import List, Dict, Any, Optional
from pydantic import BaseModel

#
# External API response item model(s)
#
class StatFinPopulationResponseDimensionsCategory(BaseModel):
    index: Dict[str, str]
    label: Dict[str, str]
    unit: Optional[Dict[str, Dict[str, Any]]]


class StatFinPopulationResponseDimensions(BaseModel):
    label: str
    category: StatFinPopulationResponseDimensionsCategory


class StatFinPopulationResponse(BaseModel):
    """
    The expected structure of the data sources item in the external API response
    --> The data source syntax"""

    label: str
    source: str
    updated: str
    dimension: Dict[str, StatFinPopulationResponseDimensions]
    id: List[str]
    size: List[int]
    value: List[int]  # the result should be in value[0]
    version: str


class StatFinFiguresResponseVariables(BaseModel):
    code: str
    text: str
    values: List[str]
    valueTexts: List[str]


class StatFinFiguresResponse(BaseModel):
    title: str
    variables: List[StatFinFiguresResponseVariables]
