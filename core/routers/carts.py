from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.products import Product, Order
from core.schemas.carts import OrderCreateUpdateSchema, OrderListSchema
from core.schemas.utils import IdListSchema
from core.services.carts import get_order_info


auth_handler = AuthHandler()
router = APIRouter(tags=["carts"])


@router.get("/order/{id}")
def fetch_order(id: int, session: Session = Depends(get_session)):
    with session:
        try:
            order = session.exec(select(Order).where(Order.id == id)).one()
            query = select(Product).where(Product.id == order.product_id)
            product = session.exec(query).one()
        except:
            raise HTTPException(status_code=404, detail="Not found")

        order_data = get_order_info(order, product)
        return order_data


@router.post("/order", response_model=OrderListSchema)
def create_order(
    *, data: OrderCreateUpdateSchema, session: Session = Depends(get_session)
):
    with session:
        order = Order(**data.dict())

        try:
            query = select(Product).where(Product.id == order.product_id)
            product = session.exec(query).one()
            print(product)
        except:
            msg = "Product ID doesn't exist"
            raise HTTPException(status_code=404, detail=msg)

        session.add(order)
        session.commit()
        session.refresh(order)
        order_data = get_order_info(order, product)
        return order_data


@router.patch("/order/bulk_delete")
def delete_order(data: IdListSchema, session: Session = Depends(get_session)):
    count = 0
    try:
        for id in data.ids:
            with session:
                statement = select(Order).where(Order.id == id)
                product = session.exec(statement).one()
                session.delete(product)
                session.commit()
                count += 1
    except:
        raise HTTPException(status_code=404, detail="Something went wrong")

    return {"detail": f"{count} Item(s) have been deleted."}


@router.get("/cart")
def fetch_cart(session: Session = Depends(get_session)):
    with session:
        products = session.exec(select(Order)).all()
