from pydantic import BaseModel, EmailStr
from app.models.user import Role


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: dict