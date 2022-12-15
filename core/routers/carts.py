from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.products import Order
from core.schemas.carts import OrderCreateUpdateSchema, OrderListSchema
from core.services.carts import get_order_info


auth_handler = AuthHandler()
router = APIRouter(tags=["carts"])


@router.get("/order/{id}")
def fetch_order(id: int, session: Session = Depends(get_session)):
    with session:
        order = session.exec(select(Order).where(Order.id == id)).one()
        return get_order_info(order)


@router.post("/order", response_model=OrderListSchema)
def create_order(
    *, data: OrderCreateUpdateSchema, session: Session = Depends(get_session)
):
    with session:
        order = Order(**data.dict())
        session.add(order)
        session.commit()
        session.refresh(order)
        order_data = get_order_info(order)
        return order_data


@router.post("/add_to_cart", response_model=None)
def add_item_to_cart(*, session: Session = Depends(get_session)):
    with session:
        print("Debug")
        return {}
