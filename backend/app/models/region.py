from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .organization import Organization


class RegionBase(SQLModel):
    name: str = Field(max_length=255, unique=True)
    code: int | None = Field(unique=True, default=None)


class Region(RegionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    organizations: list["Organization"] = Relationship(
        back_populates="region", sa_relationship_kwargs={"lazy": "selectin"}
    )
    appeals: list["Appeal"] = Relationship(
        back_populates="region", sa_relationship_kwargs={"lazy": "selectin"}
    )


class RegionRead(RegionBase):
    id: UUID


class RegionCreate(RegionBase):
    pass


class RegionUpdate(SQLModel):
    name: str | None = None
    code: int | None = None
