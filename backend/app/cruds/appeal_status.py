from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.appeal_status import AppealStatus, AppealStatusBase


def create_appeal_status(
    *,
    session: Session,
    appeal_status_in: AppealStatusBase,
) -> AppealStatus:
    """Создание статуса обращения"""
    # Проверяем уникальность имени
    existing_status = get_appeal_status_by_name(
        session=session, name=appeal_status_in.name
    )
    if existing_status:
        raise HTTPException(
            status_code=400,
            detail="Status with this name already exists",
        )

    db_appeal_status = AppealStatus.model_validate(appeal_status_in)
    session.add(db_appeal_status)
    session.commit()
    session.refresh(db_appeal_status)
    return db_appeal_status


def get_appeal_status(
    *,
    session: Session,
    appeal_status_id: UUID,
) -> AppealStatus | None:
    """Получение статуса по ID"""
    return session.get(AppealStatus, appeal_status_id)


def get_appeal_statuses(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[AppealStatus]:
    """Получение списка статусов"""
    statement = select(AppealStatus).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_appeal_status(
    *,
    session: Session,
    db_appeal_status: AppealStatus,
    appeal_status_in: AppealStatusBase,
) -> AppealStatus:
    """Обновление статуса"""
    # Проверяем уникальность имени
    if appeal_status_in.name != db_appeal_status.name:
        existing_status = get_appeal_status_by_name(
            session=session, name=appeal_status_in.name
        )
        if existing_status:
            raise HTTPException(
                status_code=400,
                detail="Status with this name already exists",
            )

    update_data = appeal_status_in.model_dump(exclude_unset=True)
    db_appeal_status.sqlmodel_update(update_data)
    session.add(db_appeal_status)
    session.commit()
    session.refresh(db_appeal_status)
    return db_appeal_status


def delete_appeal_status(
    *,
    session: Session,
    appeal_status_id: UUID,
) -> None:
    """Удаление статуса"""
    appeal_status = session.get(AppealStatus, appeal_status_id)
    if not appeal_status:
        raise HTTPException(
            status_code=404,
            detail="Appeal status not found",
        )

    # Проверяем, есть ли обращения с этим статусом
    if appeal_status.appeals:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete status that is used by appeals",
        )

    # Проверяем, используется ли статус в организациях
    if appeal_status.organizations:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete status that is used by organizations",
        )

    session.delete(appeal_status)
    session.commit()


def get_appeal_status_by_name(
    *,
    session: Session,
    name: str,
) -> AppealStatus | None:
    """Получение статуса по имени"""
    statement = select(AppealStatus).where(AppealStatus.name == name)
    return session.exec(statement).first()
