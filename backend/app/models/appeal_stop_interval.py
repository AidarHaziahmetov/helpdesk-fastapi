from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .appeal import Appeal


class AppealStopIntervalBase(SQLModel):
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: datetime | None = None


class AppealStopInterval(AppealStopIntervalBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    appeal_id: UUID = Field(foreign_key="appeal.id")

    # Relationships
    appeal: "Appeal" = Relationship(back_populates="stop_intervals")

    def __str__(self) -> str:
        return f"{self.appeal}: {self.start_date} - {self.end_date or '...'}"

    def get_duration_dates(self) -> timedelta:
        if self.end_date:
            return self.end_date - self.start_date
        return timedelta()
