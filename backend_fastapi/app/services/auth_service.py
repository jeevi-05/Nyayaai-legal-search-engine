from sqlalchemy.orm import Session

from app.models.user import User, Role
from app.schemas.auth import RegisterRequest, LoginRequest

from app.core.security import (
    hash_password,
    verify_password
)

from app.core.jwt import create_access_token



def register(
    db: Session,
    req: RegisterRequest
):

    existing_user = (
        db.query(User)
        .filter(User.email == req.email)
        .first()
    )


    if existing_user:
        raise Exception(
            "Email already registered"
        )


    user = User(

        full_name=req.full_name,

        email=req.email,

        password_hash=hash_password(
            req.password
        ),

        role=req.role if req.role else Role.CIVILIAN

    )


    db.add(user)

    db.commit()

    db.refresh(user)



    token = create_access_token(
        user.email,
        user.role.value
    )


    return {

        "token": token,

        "user": {

            "id": user.id,

            "full_name": user.full_name,

            "email": user.email,

            "role": user.role.value

        }

    }





def login(
    db: Session,
    req: LoginRequest
):


    user = (
        db.query(User)
        .filter(User.email == req.email)
        .first()
    )


    if not user:
        raise Exception(
            "Invalid credentials"
        )


    if not verify_password(
        req.password,
        user.password_hash
    ):

        raise Exception(
            "Invalid credentials"
        )


    token = create_access_token(
        user.email,
        user.role.value
    )


    return {

        "token": token,

        "user": {

            "id": user.id,

            "full_name": user.full_name,

            "email": user.email,

            "role": user.role.value

        }

    }