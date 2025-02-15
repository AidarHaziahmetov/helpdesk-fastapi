from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal
    from .department import Department
    from .organization import Organization
    from .user import User


class SpecialistOrganization(SQLModel, table=True):
    specialist_id: UUID = Field(foreign_key="specialist.id", primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", primary_key=True)

    # Relationships
    specialist: "Specialist" = Relationship(
        back_populates="organization_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    organization: "Organization" = Relationship(
        back_populates="specialists", sa_relationship_kwargs={"lazy": "selectin"}
    )


class SpecialistBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id")
    department_id: UUID | None = Field(foreign_key="department.id", default=None)


class Specialist(SpecialistBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    user: "User" = Relationship(
        back_populates="specialist", sa_relationship_kwargs={"lazy": "selectin"}
    )
    department: "Department" = Relationship(
        back_populates="specialists", sa_relationship_kwargs={"lazy": "selectin"}
    )
    responsible_appeals: list["Appeal"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "foreign(Specialist.user_id) == remote(Appeal.responsible_user_id)",
            "viewonly": True,
        }
    )
    organization_links: list["SpecialistOrganization"] = Relationship(
        back_populates="specialist", sa_relationship_kwargs={"lazy": "selectin"}
    )
