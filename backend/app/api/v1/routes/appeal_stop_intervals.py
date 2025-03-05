from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import AsyncSessionDep, get_current_active_superuser
from app.cruds.appeal_stop_interval import (
    create_appeal_stop_interval_async,
    delete_appeal_stop_interval_async,
    get_active_appeal_stop_intervals_async,
    get_appeal_stop_interval_async,
    get_appeal_stop_intervals_async,
    update_appeal_stop_interval_async,
)
from app.models.appeal_stop_interval import (
    AppealStopInterval,
    AppealStopIntervalCreate,
    AppealStopIntervalUpdate,
)
from app.models.common import Message

router = APIRouter(prefix="/appeal-stop-intervals", tags=["appeals"])


@router.get("/", response_model=list[AppealStopInterval])
async def read_appeal_stop_intervals(
    session: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> list[AppealStopInterval]:
    """
    Получить список интервалов остановки обработки обращений.
    """
    intervals = await get_appeal_stop_intervals_async(
        session=session, skip=skip, limit=limit
    )
    return intervals


@router.get("/active", response_model=list[AppealStopInterval])
async def read_active_appeal_stop_intervals(
    session: AsyncSessionDep,
    current_dt: datetime = None,
) -> list[AppealStopInterval]:
    """
    Получить список активных интервалов остановки обработки обращений.
    """
    intervals = await get_active_appeal_stop_intervals_async(
        session=session, current_dt=current_dt
    )
    return intervals


@router.post(
    "/",
    response_model=AppealStopInterval,
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_new_appeal_stop_interval(
    *,
    session: AsyncSessionDep,
    interval_in: AppealStopIntervalCreate,
) -> AppealStopInterval:
    """
    Создать новый интервал остановки обработки обращений.
    Только для суперпользователей.
    """
    interval = await create_appeal_stop_interval_async(
        session=session, interval_in=interval_in
    )
    return interval


@router.get("/{interval_id}", response_model=AppealStopInterval)
async def read_appeal_stop_interval(
    *,
    session: AsyncSessionDep,
    interval_id: UUID,
) -> AppealStopInterval:
    """
    Получить информацию о интервале остановки обработки обращений по ID.
    """
    interval = await get_appeal_stop_interval_async(
        session=session, interval_id=interval_id
    )
    if not interval:
        raise HTTPException(
            status_code=404,
            detail="Appeal stop interval not found",
        )
    return interval


@router.patch(
    "/{interval_id}",
    response_model=AppealStopInterval,
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_appeal_stop_interval_by_id(
    *,
    session: AsyncSessionDep,
    interval_id: UUID,
    interval_in: AppealStopIntervalUpdate,
) -> AppealStopInterval:
    """
    Обновить интервал остановки обработки обращений.
    Только для суперпользователей.
    """
    db_interval = await get_appeal_stop_interval_async(
        session=session, interval_id=interval_id
    )
    if not db_interval:
        raise HTTPException(
            status_code=404,
            detail="Appeal stop interval not found",
        )

    updated_interval = await update_appeal_stop_interval_async(
        session=session,
        db_interval=db_interval,
        interval_in=interval_in,
    )
    return updated_interval


@router.delete(
    "/{interval_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_appeal_stop_interval_by_id(
    *,
    session: AsyncSessionDep,
    interval_id: UUID,
) -> Message:
    """
    Удалить интервал остановки обработки обращений.
    Только для суперпользователей.
    """
    await delete_appeal_stop_interval_async(session=session, interval_id=interval_id)
    return Message(message="Appeal stop interval deleted successfully")
