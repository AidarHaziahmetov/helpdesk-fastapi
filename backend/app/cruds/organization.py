from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.appeal_status import AppealStatus
from app.models.organization import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
)
from app.models.region import Region


def create_organization(
    *,
    session: Session,
    organization_in: OrganizationCreate,
) -> Organization:
    """Создание организации"""
    # Проверяем существование региона
    region = session.get(Region, organization_in.region_id)
    if not region:
        raise HTTPException(
            status_code=400,
            detail="Region not found",
        )

    # Проверяем существование статуса завершения, если он указан
    if organization_in.custom_appeal_completion_status_id:
        status = session.get(
            AppealStatus, organization_in.custom_appeal_completion_status_id
        )
        if not status:
            raise HTTPException(
                status_code=400,
                detail="Appeal completion status not found",
            )

    db_organization = Organization.model_validate(organization_in)

    # Если custom_appeal_completion=False, убираем custom_appeal_completion_status_id
    if not db_organization.custom_appeal_completion:
        db_organization.custom_appeal_completion_status_id = None

    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


def get_organization(
    *,
    session: Session,
    organization_id: UUID,
) -> Organization | None:
    """Получение организации по ID"""
    return session.get(Organization, organization_id)


def get_organizations(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Organization]:
    """Получение списка организаций"""
    statement = select(Organization).offset(skip).limit(limit)
    organizations = session.exec(statement).all()
    return organizations


def update_organization(
    *,
    session: Session,
    db_organization: Organization,
    organization_in: OrganizationUpdate,
) -> Organization:
    """Обновление организации"""
    organization_data = organization_in.model_dump(exclude_unset=True)
    db_organization.sqlmodel_update(organization_data)
    session.add(db_organization)
    session.commit()
    session.refresh(db_organization)
    return db_organization


def delete_organization(
    *,
    session: Session,
    organization_id: UUID,
) -> None:
    """Удаление организации"""
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )
    session.delete(organization)
    session.commit()


def get_organization_by_name(
    *,
    session: Session,
    name: str,
) -> Organization | None:
    """Получение организации по названию"""
    statement = select(Organization).where(Organization.name == name)
    return session.exec(statement).first()
