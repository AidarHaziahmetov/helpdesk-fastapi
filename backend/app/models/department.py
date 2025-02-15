from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .organization import Organization
    from .specialist import Specialist


class DepartmentBase(SQLModel):
    name: str = Field(max_length=255)
    organization_id: UUID = Field(foreign_key="organization.id")


class Department(DepartmentBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    organization: "Organization" = Relationship(
        back_populates="departments", sa_relationship_kwargs={"lazy": "selectin"}
    )
    specialists: list["Specialist"] = Relationship(
        back_populates="department", sa_relationship_kwargs={"lazy": "selectin"}
    )


class DepartmentRead(DepartmentBase):
    id: UUID


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(SQLModel):
    name: str | None = None
