from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.cruds.organization import (
    create_organization,
    delete_organization,
    get_organization,
    get_organizations,
    update_organization,
)
from app.cruds.representative import get_representative_by_user_id
from app.models.common import Message
from app.models.organization import Organization, OrganizationCreate, OrganizationUpdate

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=list[Organization])
def read_organizations(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список организаций.
    Для суперпользователей - все организации.
    Для представителей - только их организация.
    """
    if current_user.is_superuser:
        organizations = get_organizations(session=session, skip=skip, limit=limit)
    else:
        representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not representative:
            return []
        organizations = [representative.organization]
    return organizations


@router.post(
    "/",
    response_model=Organization,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_new_organization(
    *,
    session: SessionDep,
    organization_in: OrganizationCreate,
) -> Any:
    """
    Создать новую организацию.
    Только для суперпользователей.
    """
    organization = create_organization(
        session=session,
        organization_in=organization_in,
    )
    return organization


@router.get("/{organization_id}", response_model=Organization)
def read_organization(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    organization_id: UUID,
) -> Any:
    """
    Получить информацию об организации по ID.
    Доступно для суперпользователей и представителей этой организации.
    """
    organization = get_organization(session=session, organization_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    if not current_user.is_superuser:
        representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not representative or representative.organization_id != organization_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to access this organization",
            )

    return organization


@router.patch("/{organization_id}", response_model=Organization)
def update_organization_by_id(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    organization_id: UUID,
    organization_in: OrganizationUpdate,
) -> Any:
    """
    Обновить организацию.
    Доступно для суперпользователей и представителей этой организации.
    Представители могут обновлять только определенные поля.
    """
    organization = get_organization(session=session, organization_id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    if not current_user.is_superuser:
        representative = get_representative_by_user_id(
            session=session, user_id=current_user.id
        )
        if not representative or representative.organization_id != organization_id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to update this organization",
            )

        # Ограничиваем поля, которые может обновлять представитель
        allowed_fields = {
            "email",
            "phone",
            "telegram_chat_id",
            "send_notifications_to_internal_chat",
        }
        update_data = organization_in.model_dump(exclude_unset=True)
        forbidden_fields = set(update_data.keys()) - allowed_fields
        if forbidden_fields:
            raise HTTPException(
                status_code=403,
                detail=f"Representatives can't update these fields: {', '.join(forbidden_fields)}",
            )

    updated_organization = update_organization(
        session=session,
        db_organization=organization,
        organization_in=organization_in,
    )
    return updated_organization


@router.delete(
    "/{organization_id}",
    response_model=Message,
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_organization_by_id(
    *,
    session: SessionDep,
    organization_id: UUID,
) -> Any:
    """
    Удалить организацию.
    Только для суперпользователей.
    """
    delete_organization(session=session, organization_id=organization_id)
    return Message(message="Organization deleted successfully")
