from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import SessionDep, get_current_active_superuser
from app.cruds.appeal_status import (
    create_appeal_status,
    delete_appeal_status,
    get_appeal_status,
    get_appeal_statuses,
    update_appeal_status,
)
from app.models.appeal_status import AppealStatus, AppealStatusBase
from app.models.common import Message

router = APIRouter(prefix="/appeal-statuses", tags=["appeal statuses"])


@router.get("/", response_model=list[AppealStatus])
def read_appeal_statuses(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список статусов обращений.
    """
    statuses = get_appeal_statuses(session=session, skip=skip, limit=limit)
    return statuses


@router.post(
    "/",
    response_model=AppealStatus,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_new_appeal_status(
    *,
    session: SessionDep,
    appeal_status_in: AppealStatusBase,
) -> Any:
    """
    Создать новый статус обращения.
    Только для суперпользователей.
    """
    status = create_appeal_status(session=session, appeal_status_in=appeal_status_in)
    return status


@router.get("/{appeal_status_id}", response_model=AppealStatus)
def read_appeal_status(
    *,
    session: SessionDep,
    appeal_status_id: UUID,
) -> Any:
    """
    Получить информацию о статусе обращения по ID.
    """
    status = get_appeal_status(session=session, appeal_status_id=appeal_status_id)
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Appeal status not found",
        )
    return status


@router.patch(
    "/{appeal_status_id}",
    response_model=AppealStatus,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_appeal_status_by_id(
    *,
    session: SessionDep,
    appeal_status_id: UUID,
    appeal_status_in: AppealStatusBase,
) -> Any:
    """
    Обновить статус обращения.
    Только для суперпользователей.
    """
    db_status = get_appeal_status(session=session, appeal_status_id=appeal_status_id)
    if not db_status:
        raise HTTPException(
            status_code=404,
            detail="Appeal status not found",
        )

    updated_status = update_appeal_status(
        session=session,
        db_appeal_status=db_status,
        appeal_status_in=appeal_status_in,
    )
    return updated_status


@router.delete(
    "/{appeal_status_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_appeal_status_by_id(
    *,
    session: SessionDep,
    appeal_status_id: UUID,
) -> Any:
    """
    Удалить статус обращения.
    Только для суперпользователей.
    Нельзя удалить статус, если он используется в обращениях или организациях.
    """
    delete_appeal_status(session=session, appeal_status_id=appeal_status_id)
    return Message(message="Appeal status deleted successfully")
