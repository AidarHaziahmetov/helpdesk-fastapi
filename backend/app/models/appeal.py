from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal_file import AppealFile
    from .appeal_status import AppealStatus
    from .appeal_stop_interval import AppealStopInterval
    from .comment import Comment
    from .region import Region
    from .task import Task
    from .user import User


class AppealBase(SQLModel):
    subject: str = Field(max_length=128, default="")
    description: str = Field(default="")
    priority: str = Field(max_length=255)
    name: str = Field(max_length=255, default="")
    surname: str = Field(max_length=255, default="")
    patronymic: str = Field(max_length=255, default="")
    phone: str = Field(max_length=20, default="")
    email: str = Field(max_length=255, default="")
    department: str = Field(max_length=255, default="")
    work_position: str = Field(max_length=255, default="")
    solving: str = Field(default="")


class Appeal(AppealBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    dt: datetime = Field(default_factory=datetime.utcnow)
    actual_date: datetime | None = None

    user_id: UUID = Field(foreign_key="user.id")
    region_id: UUID | None = Field(foreign_key="region.id")
    project_id: UUID | None = Field(foreign_key="project.id")
    status_id: UUID = Field(foreign_key="appealstatus.id")
    responsible_user_id: UUID | None = Field(foreign_key="user.id")
    standard_priority_id: UUID | None = Field(foreign_key="standardpriority.id")
    individual_priority_id: UUID | None = Field(foreign_key="individualpriority.id")

    # Relationships
    user: "User" = Relationship(
        back_populates="appeals",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Appeal.user_id == User.id, Appeal.responsible_user_id != User.id)",
        },
    )
    responsible_user: "User" = Relationship(
        back_populates="responsible_appeals",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "primaryjoin": "and_(Appeal.responsible_user_id == User.id, Appeal.user_id != User.id)",
        },
    )
    region: "Region" = Relationship(
        back_populates="appeals", sa_relationship_kwargs={"lazy": "selectin"}
    )
    status: "AppealStatus" = Relationship(
        back_populates="appeals", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tasks: list["Task"] = Relationship(back_populates="appeal")
    comments: list["Comment"] = Relationship(back_populates="appeal")
    files: list["AppealFile"] = Relationship(back_populates="appeal")
    stop_intervals: list["AppealStopInterval"] = Relationship(back_populates="appeal")
