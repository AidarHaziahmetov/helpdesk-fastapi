from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal_status import AppealStatus
    from .contract import Contract
    from .department import Department
    from .project import OrganizationProject
    from .region import Region
    from .representative import Representative
    from .specialist import SpecialistOrganization


class OrganizationBase(SQLModel):
    name: str = Field(max_length=255, default="")
    email: str = Field(max_length=255, default="")
    phone: str = Field(max_length=255, default="")
    telegram_chat_id: str | None = Field(max_length=255, default=None)
    send_notifications_to_internal_chat: bool = Field(default=True)
    call_internal_specialists: bool = Field(default=True)
    custom_appeal_completion: bool = Field(default=False)
    region_id: UUID = Field(foreign_key="region.id")


class Organization(OrganizationBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    custom_appeal_completion_status_id: UUID | None = Field(
        default=None, foreign_key="appealstatus.id"
    )

    # Relationships
    region: "Region" = Relationship(
        back_populates="organizations", sa_relationship_kwargs={"lazy": "selectin"}
    )
    departments: list["Department"] = Relationship(
        back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"}
    )
    representatives: list["Representative"] = Relationship(
        back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"}
    )
    contracts: list["Contract"] = Relationship(
        back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"}
    )
    project_links: list["OrganizationProject"] = Relationship(
        back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"}
    )
    specialists: list["SpecialistOrganization"] = Relationship(
        back_populates="organization", sa_relationship_kwargs={"lazy": "selectin"}
    )
    custom_appeal_completion_status: "AppealStatus" = Relationship(
        back_populates="organizations", sa_relationship_kwargs={"lazy": "selectin"}
    )


class OrganizationRead(OrganizationBase):
    id: UUID
    custom_appeal_completion_status_id: UUID | None


class OrganizationCreate(OrganizationBase):
    custom_appeal_completion_status_id: UUID | None = None


class OrganizationUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    telegram_chat_id: str | None = None
    send_notifications_to_internal_chat: bool | None = None
    call_internal_specialists: bool | None = None
    custom_appeal_completion: bool | None = None
    region_id: UUID | None = None
    custom_appeal_completion_status_id: UUID | None = None
