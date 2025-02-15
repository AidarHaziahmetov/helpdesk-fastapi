from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .organization import Organization


class AppealStatusBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = None
    is_final: bool = Field(default=False)
    color: str = Field(max_length=7, default="#000000")  # HEX color code


class AppealStatus(AppealStatusBase, table=True):
    __tablename__ = "appealstatus"  # Явно указываем имя таблицы

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    appeals: list["Appeal"] = Relationship(
        back_populates="status", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organizations: list["Organization"] = Relationship(
        back_populates="custom_appeal_completion_status",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
