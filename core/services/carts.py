from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from core.config.database import get_session
from core.models.products import Product


def get_order_info(order, product):
    total = (
        (product.price * order.quantity)
        + (((product.tax or 0) / 100) * product.price)
        - order.discount
        if order.discount_type == "currency"
        else (product.price * order.quantity)
        + (((product.tax or 0) / 100) * product.price)
        - (order.discount / 100 * (product.price * order.quantity))
    )
    return {
        "id": order.id,
        "timestamp": order.timestamp,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "discount": order.discount,
        "discount_type": order.discount_type,
        "total": total,
    }
