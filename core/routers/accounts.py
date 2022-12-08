from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config.auth import AuthHandler
from core.models.accounts import User
from core.schemas.accounts import RegisterUserSchema

router = APIRouter(tags=["accounts"], prefix="/accounts/auth")

auth_handler = AuthHandler()
users = []


@router.post("/login")
async def login(data: RegisterUserSchema):
    user = None
    for x in users:
        if x["username"] == data.username:
            user = x
            break
    if (user is None) or (
        not auth_handler.verify_password(data.password, user["password"])
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")

    token = auth_handler.encode_token(user["username"])
    data = {"username": user.username, "access_token": token, "token_type": "bearer"}
    return data


@router.post("/register", status_code=201)
async def register(data: RegisterUserSchema, db: Session = Depends([])):
    is_registered = db.query(User).filter(User.email == data.email).first()
    if is_registered:
        raise HTTPException(
            status_code=400,
            detail="A registered account with this email already exists.",
        )

    user = User(
        email=data.email, password=auth_handler.get_password_hash(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = auth_handler.encode_token(data={"sub": user.id})
    data = {"email": user.email, "access_token": access_token, "token_type": "bearer"}
    print(user)
    return data

    # if any(x["username"] == data.username for x in users):
    #     raise HTTPException(status_code=400, detail="Username exists")

    # hashed_password = auth_handler.get_password_hash(data.password)
    # users.append({"username": data.username, "password": hashed_password})
    # return users
