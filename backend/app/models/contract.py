from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .priority import ContractStandardPriority

if TYPE_CHECKING:
    from .organization import Organization
    from .priority import IndividualPriority


class ContractBase(SQLModel):
    is_actual: bool = Field(default=True)
    start_dt: date
    end_dt: date
    type_priorities: str = Field(max_length=255)


class Contract(ContractBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    document: str | None = Field(default=None)

    # Relationships
    organization: "Organization" = Relationship(
        back_populates="contracts", sa_relationship_kwargs={"lazy": "selectin"}
    )
    standard_priority_links: list["ContractStandardPriority"] = Relationship(
        back_populates="contract", sa_relationship_kwargs={"lazy": "selectin"}
    )
    individual_priorities: list["IndividualPriority"] = Relationship(
        back_populates="contract", sa_relationship_kwargs={"lazy": "selectin"}
    )


class ContractRead(ContractBase):
    id: UUID
    organization_id: UUID


class ContractCreate(ContractBase):
    organization_id: UUID


class ContractUpdate(SQLModel):
    is_actual: bool | None = None
    start_dt: date | None = None
    end_dt: date | None = None
    type_priorities: str | None = None
