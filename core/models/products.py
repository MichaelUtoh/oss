from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    product_no: str
    category: str
    unit: Optional[str] = None
    tax: Optional[int] = None
    price: float
    timestamp: Optional[datetime] = datetime.now()
    business_id: Optional[int] = Field(default=None, foreign_key="business.id")


class ProductImage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    timestamp: Optional[datetime] = datetime.now()
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
