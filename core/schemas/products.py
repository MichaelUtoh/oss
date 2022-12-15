from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator


class ProductCreateUpdateSchema(BaseModel):
    business_id: int
    name: str
    description: Optional[str]
    category: str
    product_no: str
    price: float
    tax: Optional[int] = None
    unit: Optional[str] = None


class ProductListSchema(BaseModel):
    id: int
    business_id: int
    name: str
    product_no: str
    category: str
    unit: Optional[str]
    tax: Optional[int] = None
    description: Optional[str]
    price: float
    timestamp: datetime = datetime.now()

    class Config:
        orm_mode = True


class ProductImageListSchema(BaseModel):
    id: int
    url: str
    product_id: int
    timestamp: datetime = datetime.now()

    class Config:
        orm_mode = True


class ProductBasicSchema(BaseModel):
    id: int
    business_id: int
    name: str
    product_no: str
    category: str
    unit: Optional[str]
    tax: Optional[int] = None
    description: Optional[str]
    price: float
    timestamp: datetime = datetime.now()
    images: List[ProductImageListSchema]

    class Config:
        orm_mode = True
