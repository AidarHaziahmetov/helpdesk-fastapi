from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.appeal_stop_interval import (
    AppealStopInterval,
    AppealStopIntervalCreate,
    AppealStopIntervalUpdate,
)

# Синхронные версии функций


def create_appeal_stop_interval(
    *,
    session: Session,
    interval_in: AppealStopIntervalCreate,
) -> AppealStopInterval:
    """Создание интервала остановки обработки обращений"""
    # Проверяем, что дата начала меньше даты окончания
    if interval_in.start_dt >= interval_in.end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    db_interval = AppealStopInterval.model_validate(interval_in)
    session.add(db_interval)
    session.commit()
    session.refresh(db_interval)
    return db_interval


def get_appeal_stop_interval(
    *,
    session: Session,
    interval_id: UUID,
) -> AppealStopInterval | None:
    """Получение интервала по ID"""
    return session.get(AppealStopInterval, interval_id)


def get_appeal_stop_intervals(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[AppealStopInterval]:
    """Получение списка интервалов"""
    statement = select(AppealStopInterval).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_active_appeal_stop_intervals(
    *,
    session: Session,
    current_dt: datetime = None,
) -> list[AppealStopInterval]:
    """Получение активных интервалов на указанную дату"""
    current_dt = current_dt or datetime.now()
    statement = select(AppealStopInterval).where(
        AppealStopInterval.start_dt <= current_dt,
        AppealStopInterval.end_dt >= current_dt,
    )
    return session.exec(statement).all()


def update_appeal_stop_interval(
    *,
    session: Session,
    db_interval: AppealStopInterval,
    interval_in: AppealStopIntervalUpdate,
) -> AppealStopInterval:
    """Обновление интервала"""
    update_data = interval_in.model_dump(exclude_unset=True)

    # Проверяем даты, если они обновляются
    start_dt = update_data.get("start_dt") or db_interval.start_dt
    end_dt = update_data.get("end_dt") or db_interval.end_dt

    if start_dt >= end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    db_interval.sqlmodel_update(update_data)
    session.add(db_interval)
    session.commit()
    session.refresh(db_interval)
    return db_interval


def delete_appeal_stop_interval(
    *,
    session: Session,
    interval_id: UUID,
) -> None:
    """Удаление интервала"""
    interval = session.get(AppealStopInterval, interval_id)
    if not interval:
        raise HTTPException(
            status_code=404,
            detail="Interval not found",
        )

    session.delete(interval)
    session.commit()


# Асинхронные версии функций


async def create_appeal_stop_interval_async(
    *,
    session: AsyncSession,
    interval_in: AppealStopIntervalCreate,
) -> AppealStopInterval:
    """Асинхронное создание интервала остановки обработки обращений"""
    # Проверяем, что дата начала меньше даты окончания
    if interval_in.start_dt >= interval_in.end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    db_interval = AppealStopInterval.model_validate(interval_in)
    session.add(db_interval)
    await session.commit()
    await session.refresh(db_interval)
    return db_interval


async def get_appeal_stop_interval_async(
    *,
    session: AsyncSession,
    interval_id: UUID,
) -> AppealStopInterval | None:
    """Асинхронное получение интервала по ID"""
    return await session.get(AppealStopInterval, interval_id)


async def get_appeal_stop_intervals_async(
    *,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[AppealStopInterval]:
    """Асинхронное получение списка интервалов"""
    statement = select(AppealStopInterval).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()


async def get_active_appeal_stop_intervals_async(
    *,
    session: AsyncSession,
    current_dt: datetime = None,
) -> list[AppealStopInterval]:
    """Асинхронное получение активных интервалов на указанную дату"""
    current_dt = current_dt or datetime.now()
    statement = select(AppealStopInterval).where(
        AppealStopInterval.start_dt <= current_dt,
        AppealStopInterval.end_dt >= current_dt,
    )
    result = await session.exec(statement)
    return result.all()


async def update_appeal_stop_interval_async(
    *,
    session: AsyncSession,
    db_interval: AppealStopInterval,
    interval_in: AppealStopIntervalUpdate,
) -> AppealStopInterval:
    """Асинхронное обновление интервала"""
    update_data = interval_in.model_dump(exclude_unset=True)

    # Проверяем даты, если они обновляются
    start_dt = update_data.get("start_dt") or db_interval.start_dt
    end_dt = update_data.get("end_dt") or db_interval.end_dt

    if start_dt >= end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    db_interval.sqlmodel_update(update_data)
    session.add(db_interval)
    await session.commit()
    await session.refresh(db_interval)
    return db_interval


async def delete_appeal_stop_interval_async(
    *,
    session: AsyncSession,
    interval_id: UUID,
) -> None:
    """Асинхронное удаление интервала"""
    interval = await session.get(AppealStopInterval, interval_id)
    if not interval:
        raise HTTPException(
            status_code=404,
            detail="Interval not found",
        )

    await session.delete(interval)
    await session.commit()
