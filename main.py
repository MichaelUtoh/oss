from decouple import config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware

from core.config.database import create_db_and_tables, engine
from core.routers import accounts, businesses, carts, products
from sqlmodel import SQLModel


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def start_application():
    app = FastAPI(title="OSS")
    configure_static(app)
    create_db_and_tables()
    return app


app = start_application()
app.add_middleware(DBSessionMiddleware, db_url=config("DATABASE_URI"))
app.include_router(accounts.router)
app.include_router(businesses.router)
app.include_router(products.router)
app.include_router(carts.router)
