from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.businesses import Business
from core.models.products import Product
from core.schemas.products import ProductListSchema
from core.schemas.businesses import BusinessCreateUpdateSchema, BusinessListSchema


auth_handler = AuthHandler()
router = APIRouter(tags=["businesses"])


@router.get("/business/{id}/products", response_model=List[ProductListSchema])
def my_products(id: int, session: Session = Depends(get_session)):
    with session:
        try:
            statement = select(Business).where(Business.id == id)
            business = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Business ID does not exist.")

        statement_2 = select(Product).where(Product.business_id == business.id)
        products = session.exec(statement_2).all()
        return products


@router.get("/business/{id}", response_model=BusinessListSchema)
def business(id: int, session: Session = Depends(get_session)):
    with session:
        try:
            statement = select(Business).where(Business.id == id)
            business = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Business ID does not exist.")
        return business


@router.get("/business", response_model=List[BusinessListSchema])
def business(session: Session = Depends(get_session)):
    with session:
        return session.exec(select(Business)).all()


@router.post("/business", response_model=BusinessListSchema)
def business(
    *,
    session: Session = Depends(get_session),
    data: BusinessCreateUpdateSchema,
):
    new_business = Business(**data.dict())
    with session:
        session.add(new_business)
        session.commit()
        session.refresh(new_business)
        return new_business
