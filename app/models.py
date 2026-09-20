import reflex as rx

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLAlchemyEnum,
    String,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    pass


class UserType(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "length(trim(username)) > 0", name="ck_users_username_nonempty"
        ),
        CheckConstraint(
            "length(trim(hashed_password)) > 0", name="ck_users_hash_nonempty"
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )
    # Invalid empty insertion defaults keep required credentials fail-closed.
    username: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True, insert_default=""
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024), nullable=False, insert_default="", repr=False
    )
    user_type: Mapped[UserType] = mapped_column(
        SQLAlchemyEnum(
            UserType,
            name="user_type",
            values_callable=lambda roles: [role.value for role in roles],
            validate_strings=True,
            create_constraint=True,
        ),
        nullable=False,
        default=UserType.USER,
        server_default=UserType.USER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        init=False,
    )
