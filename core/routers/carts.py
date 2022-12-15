from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.products import Order
from core.schemas.carts import OrderCreateUpdateSchema, OrderListSchema


auth_handler = AuthHandler()
router = APIRouter(tags=["carts"])


@router.post("/create_order", response_model=OrderListSchema)
def create_order(
    *, data: OrderCreateUpdateSchema, session: Session = Depends(get_session)
):
    with session:
        order = Order(**data.dict())
        session.add(order)
        session.commit()
        session.refresh(order)
        return order


@router.post("/add_to_cart", response_model=None)
def add_item_to_cart(*, session: Session = Depends(get_session)):
    with session:
        print("Debug")
        return {}
