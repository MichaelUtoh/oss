import csv
import codecs
from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlmodel import select, Session

from core.config.auth import AuthHandler
from core.config.database import get_session
from core.models.businesses import Business
from core.models.products import Product, ProductImage
from core.schemas.products import (
    ProductBasicSchema,
    ProductCreateUpdateSchema,
    ProductListSchema,
    ProductImageListSchema,
)
from core.schemas.utils import IdListSchema


auth_handler = AuthHandler()
router = APIRouter(tags=["products"])


@router.get("/products/{id}", response_model=ProductListSchema)
def products(id: int, session: Session = Depends(get_session)):
    with session:
        try:
            statement = select(Product).where(Product.id == id)
            product = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Product ID does not exist")
        return product


@router.get("/products", response_model=List[ProductListSchema])
def products(session: Session = Depends(get_session)):
    with session:
        return session.exec(select(Product)).all()


@router.post("/products/batch_upload")
def batch_upload(
    business_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    with session:
        try:
            statement = select(Business).where(Business.id == business_id)
            business = session.exec(statement).one()
        except:
            msg = "Business ID does not exist."
            raise HTTPException(status_code=404, detail=msg)

    if not file.filename.endswith(".csv"):
        msg = "File type must be CSV"
        raise HTTPException(status_code=404, detail=msg)

    csvReader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
    count = 0
    data = {}
    for data in csvReader:
        with session:
            product = Product(
                business_id=business_id,
                name=data["Name"],
                product_no=data["Product No."],
                description=data["Description"],
                category=data["Category"],
                tax=data["Tax"],
                unit=data["Unit"],
                price=data["Price"],
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            count += 1

    file.file.close()
    return {"detail": f"{count} Files uploaded successfully"}


@router.post("/products", response_model=ProductListSchema)
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
            raise HTTPException(
                status_code=404, detail="Product with same name already exists."
            )

        new_product = Product(**data.dict())
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product


@router.patch("/products/bulk_delete")
def products(data: IdListSchema, session: Session = Depends(get_session)):
    count = 0
    try:
        for id in data.ids:
            with session:
                statement = select(Product).where(Product.id == id)
                product = session.exec(statement).one()
                session.delete(product)
                session.commit()
                count += 1
    except:
        raise HTTPException(status_code=404, detail="Something went wrong")

    return {"detail": f"{count} Item(s) have been deleted."}


@router.put("/products/{id}")
def products(
    *,
    id: int,
    session: Session = Depends(get_session),
    product: ProductCreateUpdateSchema,
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


@router.get("/products/{id}/images", response_model=ProductBasicSchema)
def get_product_images(id: int, session: Session = Depends(get_session)):
    with session:
        try:
            statement = select(Product).where(Product.id == id)
            product = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Product ID not found.")

        product_images = session.exec(
            select(ProductImage).where(ProductImage.product_id == product.id)
        ).all()

        data = {
            "id": product.id,
            "product_no": product.product_no,
            "unit": product.unit,
            "price": product.price,
            "business_id": product.business_id,
            "description": product.description,
            "name": product.name,
            "category": product.category,
            "tax": product.tax,
            "timestamp": product.timestamp,
            "images": product_images,
        }
        return data


@router.post("/products/{id}/images")
def add_product_image(
    id: int,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session),
):
    with session:
        try:
            statement = select(Product).where(Product.id == id)
            product = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Product ID not found.")

        count = 0
        for file in files:
            res = cloudinary.uploader.upload(file.file)
            url = res.get("url")
            new_image = ProductImage(product_id=product.id, url=url)
            session.add(new_image)
            session.commit()
            session.refresh(new_image)
            count += 1
        return {"detail": f"{count} Files have been uploaded"}
