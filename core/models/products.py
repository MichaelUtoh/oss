from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str]
    price: float
    timestamp: Optional[datetime] = None

    business_id: Optional[int] = Field(default=None, foreign_key="product.id")
