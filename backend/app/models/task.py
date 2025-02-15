from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .user import User


class TaskBase(SQLModel):
    gitlab_url: str = Field(max_length=255, default="")
    status: str = Field(max_length=255)


class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appeal_id: UUID = Field(foreign_key="appeal.id")
    user_id: UUID = Field(foreign_key="user.id")
    description: str = Field(default="")

    # Relationships
    appeal: "Appeal" = Relationship(back_populates="tasks")
    user: "User" = Relationship(back_populates="tasks")
