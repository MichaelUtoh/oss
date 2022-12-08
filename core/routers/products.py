from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.businesses import Business
from core.models.products import Product
from core.schemas.products import ProductCreateUpdateSchema, ProductListSchema
from core.schemas.utils import IdListSchema


auth_handler = AuthHandler()
router = APIRouter(tags=["products"])


@router.get("/products/{id}", response_model=ProductListSchema)
def products(id: int, session: Session = Depends(get_session)):
    with session:
        statement = select(Product).where(Product.id == id)
        product = session.exec(statement).one()
        return product


@router.get("/products", response_model=List[ProductListSchema])
def products(session: Session = Depends(get_session)):
    with session:
        statement = select(Product)
        return session.exec(statement).all()


# , response_model=ProductListSchema
@router.post("/products")
def products(
    *, session: Session = Depends(get_session), data: ProductCreateUpdateSchema
):
    business = None
    product_exists = None
    with session:
        try:
            statement = select(Business).where(Business.id == data.business_id)
            business = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Business ID does not exist.")


        try:
            statement_2 = select(Product).where(Product.name == data.name)
            product_exists = session.exec(statement_2).one()
        except:
            pass

        if product_exists:
            raise HTTPException(status_code=404, detail="Product with same name already exists.")

        new_product = Product(**data.dict())
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product


@router.patch("/products/bulk_delete")
def products(data: IdListSchema, session: Session = Depends(get_session)):
    for id in data.ids:
        with session:
            statement = select(Product).where(Product.id == id)
            product = session.exec(statement).one()
            session.delete(product)
            session.commit()


@router.put("/products/{id}")
def products(
    *,
    id: int,
    session: Session = Depends(get_session),
    product: ProductCreateUpdateSchema
):
    data = Product(**product.dict())
    with session:
        statement = select(Product).where(Product.id == id)
        product = session.exec(statement).one()
        product.name = data.name
        product.description = data.description
        product.price = data.price
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
