from pydantic import BaseModel, EmailStr


class RegisterUserSchema(BaseModel):
    email: EmailStr
    password: str


class UserDetailSchema(BaseModel):
    id: int
    key: str
    email: EmailStr
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    image_url: str = None
    gender: str = None

    title: str = None
    status: str = None
    phone: str = None
    nationality: str = None

    next_of_kin_first_name: str = None
    next_of_kin_last_name: str = None
    next_of_kin_phone: str = None

    class Config:
        orm_mode = True
