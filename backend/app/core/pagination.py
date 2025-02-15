from typing import Generic, TypeVar
from uuid import UUID

from fastapi import Query
from sqlmodel import Session, SQLModel, func, select

T = TypeVar("T")


class PaginationParams(SQLModel):
    # Параметры страничной пагинации
    page: int = Query(default=1, ge=1, description="Номер страницы")
    per_page: int = Query(
        default=20, ge=1, le=100, description="Количество элементов на странице"
    )

    # Параметры курсор-пагинации
    cursor: UUID | None = Query(
        default=None, description="ID последнего элемента предыдущей страницы"
    )
    limit: int | None = None  # Если указан cursor, будет использоваться этот лимит

    def get_limit(self) -> int:
        """Возвращает актуальный размер страницы"""
        if self.cursor is not None and self.limit is not None:
            return self.limit
        return self.per_page


class PaginatedResponse(SQLModel, Generic[T]):
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


def paginate_query(
    session: Session,
    query: select,
    params: PaginationParams,
) -> PaginatedResponse:
    """
    Универсальная функция пагинации для SQLModel запросов

    Поддерживает как страничную, так и курсор-пагинацию
    """
    # Если используется курсор-пагинация
    if params.cursor:
        # Не делаем запрос для подсчета total
        query = query.where(query.primary_key > params.cursor)
        items = session.exec(query.limit(params.get_limit())).all()

        has_next = len(items) == params.get_limit()
        next_cursor = items[-1].id if has_next and items else None

        return PaginatedResponse(
            items=items, has_next=has_next, next_cursor=next_cursor
        )

    # Для страничной пагинации считаем total
    total = session.exec(select(func.count()).select_from(query.subquery())).one()

    # Страничная пагинация
    items = session.exec(
        query.offset((params.page - 1) * params.per_page).limit(params.per_page)
    ).all()

    total_pages = (total + params.per_page - 1) // params.per_page

    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        per_page=params.per_page,
        total_pages=total_pages,
        has_prev=params.page > 1,
        has_next=params.page < total_pages,
    )
