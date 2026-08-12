import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Enum, DateTime

from app.core.database import Base


class Role(str, enum.Enum):

    CIVILIAN = "CIVILIAN"
    LAWYER = "LAWYER"
    JUDGE = "JUDGE"
    POLICE = "POLICE"
    ADMIN = "ADMIN"



class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )


    full_name = Column(
        String,
        nullable=False
    )


    email = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )


    password_hash = Column(
        String,
        nullable=False
    )


    role = Column(
        Enum(Role),
        nullable=False,
        default=Role.CIVILIAN
    )


    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )