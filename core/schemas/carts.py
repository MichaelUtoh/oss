from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.models.products import DiscountTypeEnum


class OrderListSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    discount: float
    discount_type: Optional[str] = DiscountTypeEnum.currency
    timestamp: Optional[datetime] = datetime.now()


class OrderCreateUpdateSchema(BaseModel):
    product_id: int
    quantity: int
    discount: float
    discount_type: Optional[str] = DiscountTypeEnum.currency
