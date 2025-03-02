from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import AsyncSessionDep, get_current_active_superuser
from app.cruds.region import (
    create_region_async,
    delete_region_async,
    get_region_async,
    get_regions_async,
    update_region_async,
)
from app.models.common import Message
from app.models.region import Region, RegionCreate, RegionUpdate

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/", response_model=list[Region])
async def read_regions(
    session: AsyncSessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список регионов.
    """
    regions = await get_regions_async(session=session, skip=skip, limit=limit)
    return regions


@router.post(
    "/",
    response_model=Region,
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_new_region(
    *,
    session: AsyncSessionDep,
    region_in: RegionCreate,
) -> Any:
    """
    Создать новый регион.
    Только для суперпользователей.
    """
    region = await create_region_async(session=session, region_in=region_in)
    return region


@router.get("/{region_id}", response_model=Region)
async def read_region(
    *,
    session: AsyncSessionDep,
    region_id: UUID,
) -> Any:
    """
    Получить информацию о регионе по ID.
    """
    region = await get_region_async(session=session, region_id=region_id)
    if not region:
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )
    return region


@router.patch(
    "/{region_id}",
    response_model=Region,
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_region_by_id(
    *,
    session: AsyncSessionDep,
    region_id: UUID,
    region_in: RegionUpdate,
) -> Any:
    """
    Обновить регион.
    Только для суперпользователей.
    """
    db_region = await get_region_async(session=session, region_id=region_id)
    if not db_region:
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    updated_region = await update_region_async(
        session=session,
        db_region=db_region,
        region_in=region_in,
    )
    return updated_region


@router.delete(
    "/{region_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_region_by_id(
    *,
    session: AsyncSessionDep,
    region_id: UUID,
) -> Any:
    """
    Удалить регион.
    Только для суперпользователей.
    Нельзя удалить регион, если к нему привязаны организации.
    """
    await delete_region_async(session=session, region_id=region_id)
    return Message(message="Region deleted successfully")
