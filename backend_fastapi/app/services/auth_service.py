import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.models.pending_registration import PendingRegistration
from app.models.user import Role, User
from app.schemas.auth import LoginRequest, RegisterRequest, ResendOtpRequest, VerifyOtpRequest
from app.services.email_service import send_verification_email


OTP_LIFETIME = timedelta(minutes=5)
RESEND_COOLDOWN = timedelta(seconds=60)
MAX_OTP_ATTEMPTS = 5


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _normalized_email(email: str) -> str:
    return email.strip().lower()


def _masked_email(email: str) -> str:
    local, domain = email.split("@", 1)
    return f"{local[:1]}{'*' * max(1, len(local) - 1)}@{domain}"


def _auth_response(user: User) -> dict:
    return {
        "token": create_access_token(user.email, user.role.value),
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.value,
        },
    }


def _new_otp() -> str:
    return str(secrets.randbelow(9000) + 1000)


def register(db: Session, req: RegisterRequest) -> dict:
    email = _normalized_email(str(req.email))
    full_name = req.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required")
    if req.role == Role.POLICE:
        raise HTTPException(status_code=400, detail="Police registration is not available.")

    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists. Please sign in.")

    pending = db.query(PendingRegistration).filter(func.lower(PendingRegistration.email) == email).first()
    if pending:
        db.delete(pending)
        db.flush()

    otp = _new_otp()
    now = _now()
    pending = PendingRegistration(
        full_name=full_name,
        email=email,
        password_hash=hash_password(req.password),
        role=req.role,
        otp_hash=hash_password(otp),
        expires_at=now + OTP_LIFETIME,
        last_sent_at=now,
        attempt_count=0,
    )
    db.add(pending)
    db.flush()

    try:
        send_verification_email(email, full_name, otp)
        db.commit()
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Email verification is not configured. Add the backend SMTP settings and try again.") from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="We couldn't send the verification email right now. Please try again.") from exc

    return {"requires_verification": True, "email": _masked_email(email)}


def verify_otp(db: Session, req: VerifyOtpRequest) -> dict:
    email = _normalized_email(str(req.email))
    if not re.fullmatch(r"\d{4}", req.otp):
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please try again.")

    pending = db.query(PendingRegistration).filter(func.lower(PendingRegistration.email) == email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending email verification found.")

    now = _now()
    expires_at = pending.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        db.delete(pending)
        db.commit()
        raise HTTPException(status_code=400, detail="This verification code has expired. Please request a new code.")

    if pending.attempt_count >= MAX_OTP_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many incorrect attempts. Please request a new code.")

    if not verify_password(req.otp, pending.otp_hash):
        pending.attempt_count += 1
        db.commit()
        if pending.attempt_count >= MAX_OTP_ATTEMPTS:
            raise HTTPException(status_code=429, detail="Too many incorrect attempts. Please request a new code.")
        raise HTTPException(status_code=400, detail="Incorrect verification code. Please try again.")

    user = User(
        full_name=pending.full_name,
        email=pending.email,
        password_hash=pending.password_hash,
        role=pending.role,
    )
    db.add(user)
    db.delete(pending)
    db.commit()
    db.refresh(user)
    return _auth_response(user)


def resend_otp(db: Session, req: ResendOtpRequest) -> dict:
    email = _normalized_email(str(req.email))
    pending = db.query(PendingRegistration).filter(func.lower(PendingRegistration.email) == email).first()
    if not pending:
        raise HTTPException(status_code=404, detail="No pending email verification found.")

    last_sent_at = pending.last_sent_at
    if last_sent_at.tzinfo is None:
        last_sent_at = last_sent_at.replace(tzinfo=timezone.utc)
    remaining = int((last_sent_at + RESEND_COOLDOWN - _now()).total_seconds())
    if remaining > 0:
        raise HTTPException(status_code=429, detail=f"Resend available in {remaining} seconds.")

    otp = _new_otp()
    pending.otp_hash = hash_password(otp)
    pending.expires_at = _now() + OTP_LIFETIME
    pending.last_sent_at = _now()
    pending.attempt_count = 0
    try:
        send_verification_email(pending.email, pending.full_name, otp)
        db.commit()
    except RuntimeError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Email verification is not configured. Add the backend SMTP settings and try again.") from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="We couldn't send the verification email right now. Please try again.") from exc

    return {"requires_verification": True, "email": _masked_email(email)}


def login(db: Session, req: LoginRequest) -> dict:
    email = _normalized_email(str(req.email))
    user = db.query(User).filter(func.lower(User.email) == email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _auth_response(user)
