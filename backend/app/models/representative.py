from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .organization import Organization
    from .user import User


class RepresentativeBase(SQLModel):
    surname: str = Field(max_length=255)
    name: str = Field(max_length=255)
    patronymic: str = Field(max_length=255, default="")
    email: str = Field(max_length=255, default="")
    phone: str = Field(max_length=255, default="")
    is_shared: bool = Field(default=False)


class Representative(RepresentativeBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    organization_id: UUID = Field(foreign_key="organization.id")
    main_representative_id: UUID | None = Field(
        foreign_key="representative.id", default=None
    )

    # Relationships
    user: "User" = Relationship(back_populates="representative")
    organization: "Organization" = Relationship(back_populates="representatives")
    main_representative: Optional["Representative"] = Relationship(
        back_populates="representatives",
        sa_relationship_kwargs={"remote_side": "Representative.id"},
    )
    representatives: list["Representative"] = Relationship(
        back_populates="main_representative"
    )
