from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .organization import Organization


class OrganizationProject(SQLModel, table=True):
    organization_id: UUID = Field(foreign_key="organization.id", primary_key=True)
    project_id: UUID = Field(foreign_key="project.id", primary_key=True)

    # Relationships
    organization: "Organization" = Relationship(
        back_populates="project_links", sa_relationship_kwargs={"lazy": "selectin"}
    )
    project: "Project" = Relationship(
        back_populates="organization_links", sa_relationship_kwargs={"lazy": "selectin"}
    )


class ProjectBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = None


class Project(ProjectBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    organization_links: list[OrganizationProject] = Relationship(
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )
