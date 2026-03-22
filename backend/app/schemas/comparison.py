from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class CompareRequest(BaseModel):
    version_a_id: int
    version_b_id: int


class ComparisonResultResponse(BaseModel):
    id: int
    version_a_id: int
    version_b_id: int
    comparison_type: str
    diff_data: Any
    summary: str
    computed_at: datetime

    model_config = {"from_attributes": True}
