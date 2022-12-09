from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProductCreateUpdateSchema(BaseModel):
    business_id: int
    name: str
    description: Optional[str]
    price: float


class ProductListSchema(BaseModel):
    id: int
    business_id: int
    name: str
    product_no: str
    category: str
    unit: Optional[str]
    tax: Optional[int]
    description: Optional[str]
    price: float
    timestamp: datetime = datetime.now()

    class Config:
        orm_mode = True
