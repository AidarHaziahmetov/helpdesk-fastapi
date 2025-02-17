from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import SessionDep, get_current_active_superuser
from app.cruds.region import (
    create_region,
    delete_region,
    get_region,
    get_regions,
    update_region,
)
from app.models.common import Message
from app.models.region import Region, RegionCreate, RegionUpdate

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/", response_model=list[Region])
def read_regions(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список регионов.
    """
    regions = get_regions(session=session, skip=skip, limit=limit)
    return regions


@router.post(
    "/",
    response_model=Region,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_new_region(
    *,
    session: SessionDep,
    region_in: RegionCreate,
) -> Any:
    """
    Создать новый регион.
    Только для суперпользователей.
    """
    region = create_region(session=session, region_in=region_in)
    return region


@router.get("/{region_id}", response_model=Region)
def read_region(
    *,
    session: SessionDep,
    region_id: UUID,
) -> Any:
    """
    Получить информацию о регионе по ID.
    """
    region = get_region(session=session, region_id=region_id)
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
def update_region_by_id(
    *,
    session: SessionDep,
    region_id: UUID,
    region_in: RegionUpdate,
) -> Any:
    """
    Обновить регион.
    Только для суперпользователей.
    """
    db_region = get_region(session=session, region_id=region_id)
    if not db_region:
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    updated_region = update_region(
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
def delete_region_by_id(
    *,
    session: SessionDep,
    region_id: UUID,
) -> Any:
    """
    Удалить регион.
    Только для суперпользователей.
    Нельзя удалить регион, если к нему привязаны организации.
    """
    delete_region(session=session, region_id=region_id)
    return Message(message="Region deleted successfully")
