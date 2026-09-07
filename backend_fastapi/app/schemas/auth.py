from pydantic import BaseModel, EmailStr
from app.models.user import Role


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Role


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResendOtpRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: dict