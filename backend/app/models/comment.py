from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .comment_file import CommentFile
    from .user import User


class CommentBase(SQLModel):
    text: str = Field(default="")


class Comment(CommentBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appeal_id: UUID = Field(foreign_key="appeal.id")
    user_id: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    appeal: "Appeal" = Relationship(back_populates="comments")
    user: "User" = Relationship(back_populates="comments")
    comment_files: list["CommentFile"] = Relationship(back_populates="comment")
