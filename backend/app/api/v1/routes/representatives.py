from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.cruds.representative import (
    create_representative,
    delete_representative,
    get_organization_representatives,
    get_representative,
    get_representative_by_user_id,
    get_representatives,
    get_subordinate_representatives,
    update_representative,
)
from app.models.common import Message
from app.models.representative import Representative, RepresentativeBase

router = APIRouter(prefix="/representatives", tags=["representatives"])


@router.get("/", response_model=list[Representative])
def read_representatives(
    session: SessionDep,
    current_user: CurrentUser,
    organization_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список представителей.
    Для суперпользователей - все представители или представители конкретной организации.
    Для представителей - только представители своей организации.
    """
    if current_user.is_superuser:
        representatives = get_representatives(
            session=session,
            organization_id=organization_id,
            skip=skip,
            limit=limit,
        )
    else:
        representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not representative:
            return []
        representatives = get_organization_representatives(
            session=session,
            organization_id=representative.organization_id,
            skip=skip,
            limit=limit,
        )
    return representatives


@router.post(
    "/",
    response_model=Representative,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_new_representative(
    *,
    session: SessionDep,
    representative_in: RepresentativeBase,
    user_id: UUID,
    organization_id: UUID,
    main_representative_id: UUID | None = None,
) -> Any:
    """
    Создать нового представителя.
    Только для суперпользователей.
    """
    if main_representative_id:
        main_rep = get_representative(
            session=session, representative_id=main_representative_id
        )
        if not main_rep or main_rep.organization_id != organization_id:
            raise HTTPException(
                status_code=400,
                detail="Main representative must belong to the same organization",
            )

    representative = create_representative(
        session=session,
        representative_in=representative_in,
        user_id=user_id,
        organization_id=organization_id,
        main_representative_id=main_representative_id,
    )
    return representative


@router.get("/{representative_id}", response_model=Representative)
def read_representative(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    representative_id: UUID,
) -> Any:
    """
    Получить информацию о представителе по ID.
    Доступно для суперпользователей и представителей той же организации.
    """
    representative = get_representative(
        session=session, representative_id=representative_id
    )
    if not representative:
        raise HTTPException(
            status_code=404,
            detail="Representative not found",
        )

    if not current_user.is_superuser:
        current_representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if (
            not current_representative
            or current_representative.organization_id != representative.organization_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to access this representative",
            )

    return representative


@router.patch("/{representative_id}", response_model=Representative)
def update_representative_by_id(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    representative_id: UUID,
    representative_in: RepresentativeBase,
) -> Any:
    """
    Обновить представителя.
    Суперпользователи могут обновлять любого представителя.
    Представители могут обновлять только свои данные.
    """
    db_representative = get_representative(
        session=session, representative_id=representative_id
    )
    if not db_representative:
        raise HTTPException(
            status_code=404,
            detail="Representative not found",
        )

    if not current_user.is_superuser:
        current_representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not current_representative or current_representative.id != representative_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this representative",
            )

    updated_representative = update_representative(
        session=session,
        db_representative=db_representative,
        representative_in=representative_in,
    )
    return updated_representative


@router.delete(
    "/{representative_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_representative_by_id(
    *,
    session: SessionDep,
    representative_id: UUID,
) -> Any:
    """
    Удалить представителя.
    Только для суперпользователей.
    """
    delete_representative(session=session, representative_id=representative_id)
    return Message(message="Representative deleted successfully")


@router.get("/{representative_id}/subordinates", response_model=list[Representative])
def read_subordinate_representatives(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    representative_id: UUID,
) -> Any:
    """
    Получить список подчиненных представителей.
    Доступно для суперпользователей и самого представителя.
    """
    representative = get_representative(
        session=session, representative_id=representative_id
    )
    if not representative:
        raise HTTPException(
            status_code=404,
            detail="Representative not found",
        )

    if not current_user.is_superuser:
        current_representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not current_representative or current_representative.id != representative_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to access subordinates",
            )

    return get_subordinate_representatives(
        session=session, main_representative_id=representative_id
    )
