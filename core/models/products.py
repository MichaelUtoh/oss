from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class DiscountTypeEnum(str, Enum):
    currency = "currency"
    percentage = "percentage"


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


class OrderCartLink(SQLModel, table=True):
    cart_id: Optional[int] = Field(
        default=None, foreign_key="cart.id", primary_key=True
    )
    order_id: Optional[int] = Field(
        default=None, foreign_key="order.id", primary_key=True
    )


class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    timestamp: Optional[datetime] = datetime.now()
    orders: List["Order"] = Relationship(
        back_populates="carts", link_model=OrderCartLink
    )


class Order(SQLModel, table=True):
    # user: authenticated_user
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    discount: float
    discount_type: Optional[str] = DiscountTypeEnum.currency
    timestamp: Optional[datetime] = datetime.now()
    carts: List[Cart] = Relationship(back_populates="orders", link_model=OrderCartLink)
