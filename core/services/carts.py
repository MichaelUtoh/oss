from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from core.config.database import get_session
from core.models.products import Product


def get_order_info(data, session: Session = Depends(get_session)):
    with session:
        try:
            query = select(Product).where(Product.id == data.product_id)
            print(query)
    #         product = session.exec(query).one()
        except:
            msg = "Product ID doesn't exist"
            raise HTTPException(status_code=404, detail=msg)
    #     print(product)

    # total = product.price
    return {
        "id": data.id,
        "discount": data.discount,
        "timestamp": data.timestamp,
        "product_id": data.product_id,
        "quantity": data.quantity,
        "discount_type": data.discount_type,
        "total": 0,
    }
