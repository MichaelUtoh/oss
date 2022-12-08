from typing import Optional
from uuid import uuid4

from pydantic import EmailStr

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = uuid4
    email: EmailStr
    password: str

    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    image_url: Optional[str] = None
    gender: str

    title: str
    status: Optional[str] = None
    phone: str
    nationality: str

    next_of_kin_first_name: Optional[str] = None
    next_of_kin_last_name: Optional[str] = None
    next_of_kin_phone: Optional[str] = None

    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
