from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal


class AppealFileBase(SQLModel):
    file: str = Field(max_length=255)


class AppealFile(AppealFileBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appeal_id: UUID | None = Field(foreign_key="appeal.id", default=None)

    # Relationships
    appeal: "Appeal" = Relationship(back_populates="files")

    def get_absolute_file_url(self) -> str:
        return f"/uploads/appeal/{self.file}"

    def get_filename(self) -> str:
        return self.file.split("/")[-1]
