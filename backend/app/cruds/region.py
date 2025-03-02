from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.region import Region, RegionCreate, RegionUpdate


def create_region(
    *,
    session: Session,
    region_in: RegionCreate,
) -> Region:
    """Создание региона"""
    # Проверяем уникальность имени
    if region_in.name:
        existing_region = get_region_by_name(session=session, name=region_in.name)
        if existing_region:
            raise HTTPException(
                status_code=400,
                detail="Region with this name already exists",
            )

    # Проверяем уникальность кода
    if region_in.code:
        existing_region = get_region_by_code(session=session, code=region_in.code)
        if existing_region:
            raise HTTPException(
                status_code=400,
                detail="Region with this code already exists",
            )

    db_region = Region.model_validate(region_in)
    session.add(db_region)
    session.commit()
    session.refresh(db_region)
    return db_region


def get_region(
    *,
    session: Session,
    region_id: UUID,
) -> Region | None:
    """Получение региона по ID"""
    return session.get(Region, region_id)


def get_regions(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Region]:
    """Получение списка регионов"""
    statement = select(Region).offset(skip).limit(limit)
    regions = session.exec(statement).all()
    return regions


def update_region(
    *,
    session: Session,
    db_region: Region,
    region_in: RegionUpdate,
) -> Region:
    """Обновление региона"""
    update_data = region_in.model_dump(exclude_unset=True)

    # Проверяем уникальность имени
    if "name" in update_data:
        existing_region = get_region_by_name(session=session, name=update_data["name"])
        if existing_region and existing_region.id != db_region.id:
            raise HTTPException(
                status_code=400,
                detail="Region with this name already exists",
            )

    # Проверяем уникальность кода
    if "code" in update_data:
        existing_region = get_region_by_code(session=session, code=update_data["code"])
        if existing_region and existing_region.id != db_region.id:
            raise HTTPException(
                status_code=400,
                detail="Region with this code already exists",
            )

    db_region.sqlmodel_update(update_data)
    session.add(db_region)
    session.commit()
    session.refresh(db_region)
    return db_region


def delete_region(
    *,
    session: Session,
    region_id: UUID,
) -> None:
    """Удаление региона"""
    region = session.get(Region, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    # Проверяем, есть ли связанные организации
    if region.organizations:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete region with linked organizations",
        )

    session.delete(region)
    session.commit()


def get_region_by_name(
    *,
    session: Session,
    name: str,
) -> Region | None:
    """Получение региона по названию"""
    statement = select(Region).where(Region.name == name)
    return session.exec(statement).first()


def get_region_by_code(
    *,
    session: Session,
    code: int,
) -> Region | None:
    """Получение региона по коду"""
    statement = select(Region).where(Region.code == code)
    return session.exec(statement).first()


async def create_region_async(
    *,
    session: AsyncSession,
    region_in: RegionCreate,
) -> Region:
    """Асинхронное создание региона"""
    # Проверяем уникальность имени
    if region_in.name:
        existing_region = await get_region_by_name_async(
            session=session, name=region_in.name
        )
        if existing_region:
            raise HTTPException(
                status_code=400,
                detail="Region with this name already exists",
            )

    # Проверяем уникальность кода
    if region_in.code:
        existing_region = await get_region_by_code_async(
            session=session, code=region_in.code
        )
        if existing_region:
            raise HTTPException(
                status_code=400,
                detail="Region with this code already exists",
            )

    db_region = Region.model_validate(region_in)
    session.add(db_region)
    await session.commit()
    await session.refresh(db_region)
    return db_region


async def get_region_async(
    *,
    session: AsyncSession,
    region_id: UUID,
) -> Region | None:
    """Асинхронное получение региона по ID"""
    return await session.get(Region, region_id)


async def get_regions_async(
    *,
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Region]:
    """Асинхронное получение списка регионов"""
    statement = select(Region).offset(skip).limit(limit)
    result = await session.exec(statement)
    return await result.all()


async def update_region_async(
    *,
    session: AsyncSession,
    db_region: Region,
    region_in: RegionUpdate,
) -> Region:
    """Асинхронное обновление региона"""
    update_data = region_in.model_dump(exclude_unset=True)

    # Проверяем уникальность имени
    if "name" in update_data:
        existing_region = await get_region_by_name_async(
            session=session, name=update_data["name"]
        )
        if existing_region and existing_region.id != db_region.id:
            raise HTTPException(
                status_code=400,
                detail="Region with this name already exists",
            )

    # Проверяем уникальность кода
    if "code" in update_data:
        existing_region = await get_region_by_code_async(
            session=session, code=update_data["code"]
        )
        if existing_region and existing_region.id != db_region.id:
            raise HTTPException(
                status_code=400,
                detail="Region with this code already exists",
            )

    db_region.sqlmodel_update(update_data)
    session.add(db_region)
    await session.commit()
    await session.refresh(db_region)
    return db_region


async def delete_region_async(
    *,
    session: AsyncSession,
    region_id: UUID,
) -> None:
    """Асинхронное удаление региона"""
    region = await session.get(Region, region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    # Проверяем, есть ли связанные организации
    if region.organizations:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete region with linked organizations",
        )

    await session.delete(region)
    await session.commit()


async def get_region_by_name_async(
    *,
    session: AsyncSession,
    name: str,
) -> Region | None:
    """Асинхронное получение региона по названию"""
    statement = select(Region).where(Region.name == name)
    result = await session.exec(statement)
    return await result.first()


async def get_region_by_code_async(
    *,
    session: AsyncSession,
    code: int,
) -> Region | None:
    """Асинхронное получение региона по коду"""
    statement = select(Region).where(Region.code == code)
    result = await session.exec(statement)
    return await result.first()
