from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal


class AppealStopIntervalBase(SQLModel):
    start_dt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    end_dt: datetime | None = None
    description: str | None = None


class AppealStopIntervalCreate(AppealStopIntervalBase):
    pass


class AppealStopIntervalUpdate(SQLModel):
    start_dt: datetime | None = None
    end_dt: datetime | None = None
    description: str | None = None


class AppealStopInterval(AppealStopIntervalBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appeal_id: UUID = Field(foreign_key="appeal.id")

    # Relationships
    appeal: "Appeal" = Relationship(back_populates="stop_intervals")

    def __str__(self) -> str:
        return f"{self.appeal}: {self.start_dt} - {self.end_dt or '...'}"

    def get_duration(self) -> timedelta:
        if self.end_dt:
            return self.end_dt - self.start_dt
        return timedelta()
