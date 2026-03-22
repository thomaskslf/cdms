from datetime import datetime
from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str


class CustomerUpdate(BaseModel):
    name: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}
