from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .comment import Comment


class CommentFileBase(SQLModel):
    file: str = Field(max_length=255)


class CommentFile(CommentFileBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    comment_id: UUID = Field(foreign_key="comment.id")

    # Relationships
    comment: "Comment" = Relationship(back_populates="comment_files")

    def get_absolute_file_url(self) -> str:
        return f"/uploads/comment/{self.file}"

    def get_filename(self) -> str:
        return self.file.split("/")[-1]
