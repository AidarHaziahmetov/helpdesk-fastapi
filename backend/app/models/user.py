from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .comment import Comment
    from .representative import Representative
    from .specialist import Specialist
    from .task import Task


# Shared properties
class UserBase(SQLModel):
    email: str = Field(max_length=255, unique=True, index=True)
    full_name: str | None = None
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    first_name: str = Field(max_length=255, default="")
    last_name: str = Field(max_length=255, default="")


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    hashed_password: str

    # Relationships
    tasks: list["Task"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    appeals: list["Appeal"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Appeal.user_id == User.id, Appeal.responsible_user_id != User.id)",
        },
    )
    responsible_appeals: list["Appeal"] = Relationship(
        back_populates="responsible_user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Appeal.responsible_user_id == User.id, Appeal.user_id != User.id)",
        },
    )
    specialist: "Specialist" = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    representative: Optional["Representative"] = Relationship(back_populates="user")
    comments: list["Comment"] = Relationship(back_populates="user")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserRead(UserBase):
    id: UUID
