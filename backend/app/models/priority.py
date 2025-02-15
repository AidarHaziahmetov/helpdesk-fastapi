from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .contract import Contract


class BasePriorityBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = None
    hours: int = Field(default=24)


class ContractStandardPriority(SQLModel, table=True):
    contract_id: UUID = Field(foreign_key="contract.id", primary_key=True)
    priority_id: UUID = Field(foreign_key="standardpriority.id", primary_key=True)

    # Relationships
    contract: "Contract" = Relationship(
        back_populates="standard_priority_links",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    priority: "StandardPriority" = Relationship(
        back_populates="contract_links", sa_relationship_kwargs={"lazy": "selectin"}
    )


class StandardPriority(BasePriorityBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationships
    contract_links: list["ContractStandardPriority"] = Relationship(
        back_populates="priority", sa_relationship_kwargs={"lazy": "selectin"}
    )


class IndividualPriority(BasePriorityBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    contract_id: UUID = Field(foreign_key="contract.id")

    # Relationships
    contract: "Contract" = Relationship(
        back_populates="individual_priorities",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
