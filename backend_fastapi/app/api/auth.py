from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, ResendOtpRequest, VerifyOtpRequest
from app.schemas.dashboard import ApiResponse

from app.services import auth_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)



@router.post("/register")
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db)
):

    data = auth_service.register(
        db,
        req
    )


    return ApiResponse(
        success=True,
        message="Verification code sent",
        data=data
    )


@router.post("/verify-otp")
def verify_otp(req: VerifyOtpRequest, db: Session = Depends(get_db)):
    data = auth_service.verify_otp(db, req)
    return ApiResponse(success=True, message="Email verified successfully", data=data)


@router.post("/resend-otp")
def resend_otp(req: ResendOtpRequest, db: Session = Depends(get_db)):
    data = auth_service.resend_otp(db, req)
    return ApiResponse(success=True, message="Verification code sent", data=data)




@router.post("/login")
def login(
    req: LoginRequest,
    db: Session = Depends(get_db)
):

    data = auth_service.login(
        db,
        req
    )


    return ApiResponse(
        success=True,
        message="Login successful",
        data=data
    )