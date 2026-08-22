from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.jwt import decode_token
from app.models.user import User, Role
from app.repositories import user_repository

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email is None:
            raise JWTError("Subject missing from token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = user_repository.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_judge(current_user: User = Depends(get_current_user)) -> User:
    """Guard the judicial-intelligence surface from all non-judge roles."""
    if current_user.role != Role.JUDGE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Judge access required")
    return current_user


def require_role(*allowed_roles):
    """Dependency to require specific user roles."""
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this feature."
            )
        return current_user
    return dependency
