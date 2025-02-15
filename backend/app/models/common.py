from typing import Generic, TypeVar
from uuid import UUID

from pydantic import Field
from sqlmodel import SQLModel

T = TypeVar("T")


class UniversalPaginationParams(SQLModel):
    # Параметры страничной пагинации
    page: int | None = Field(default=1, ge=1, description="Номер страницы")
    per_page: int | None = Field(
        default=20, ge=1, le=100, description="Количество элементов на странице"
    )

    # Параметры курсор-пагинации
    cursor: UUID | None = Field(
        default=None, description="ID последнего элемента предыдущей страницы"
    )
    limit: int | None = None  # Если указан cursor, будет использоваться этот лимит

    def get_limit(self) -> int:
        """Возвращает актуальный размер страницы"""
        if self.cursor is not None and self.limit is not None:
            return self.limit
        return self.per_page


class UniversalPaginatedResponse(SQLModel, Generic[T]):
    items: list[T]
    # Поля для страничной пагинации
    total: int | None = None
    page: int | None = None
    per_page: int | None = None
    total_pages: int | None = None
    has_prev: bool | None = None
    # Поля для курсор-пагинации
    next_cursor: UUID | None = None
    has_next: bool


class Message(SQLModel):
    message: str


class ErrorResponse(SQLModel):
    detail: str
