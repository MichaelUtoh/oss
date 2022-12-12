import cloudinary
from decouple import config
from sqlmodel import SQLModel, create_engine, Session


cloudinary.config(
    cloud_name=config("CLOUD_NAME"),
    api_key=config("CLOUDINARY_API_KEY"),
    api_secret=config("CLOUDINARY_API_SECRET"),
)


engine = create_engine(config("DB_URL"), connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
