from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.specialist import (
    Specialist,
    SpecialistBase,
    SpecialistOrganization,
)
from app.models.user import User


def create_specialist(
    *,
    session: Session,
    specialist_in: SpecialistBase,
    organization_ids: list[UUID] | None = None,
) -> Specialist:
    """Создание специалиста"""
    # Проверяем существование пользователя
    user = session.get(User, specialist_in.user_id)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User not found",
        )

    # Проверяем, что пользователь еще не является специалистом
    existing_specialist = get_specialist_by_user_id(
        session=session, user_id=specialist_in.user_id
    )
    if existing_specialist:
        raise HTTPException(
            status_code=400,
            detail="User is already a specialist",
        )

    db_specialist = Specialist.model_validate(specialist_in)
    session.add(db_specialist)
    session.commit()
    session.refresh(db_specialist)

    # Добавляем связи с организациями
    if organization_ids:
        for org_id in organization_ids:
            specialist_org = SpecialistOrganization(
                specialist_id=db_specialist.id,
                organization_id=org_id,
            )
            session.add(specialist_org)
        session.commit()
        session.refresh(db_specialist)

    return db_specialist


def get_specialist(
    *,
    session: Session,
    specialist_id: UUID,
) -> Specialist | None:
    """Получение специалиста по ID"""
    return session.get(Specialist, specialist_id)


def get_specialists(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Specialist]:
    """Получение списка специалистов"""
    statement = select(Specialist).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_specialist_by_user_id(
    *,
    session: Session,
    user_id: UUID,
) -> Specialist | None:
    """Получение специалиста по ID пользователя"""
    statement = select(Specialist).where(Specialist.user_id == user_id)
    return session.exec(statement).first()


def get_organization_specialists(
    *,
    session: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Specialist]:
    """Получение списка специалистов организации"""
    statement = (
        select(Specialist)
        .join(SpecialistOrganization)
        .where(SpecialistOrganization.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def update_specialist(
    *,
    session: Session,
    db_specialist: Specialist,
    department_id: UUID | None = None,
    organization_ids: list[UUID] | None = None,
) -> Specialist:
    """Обновление специалиста"""
    if department_id is not None:
        db_specialist.department_id = department_id

    # Обновляем связи с организациями
    if organization_ids is not None:
        # Удаляем старые связи
        statement = select(SpecialistOrganization).where(
            SpecialistOrganization.specialist_id == db_specialist.id
        )
        existing_links = session.exec(statement).all()
        for link in existing_links:
            session.delete(link)

        # Добавляем новые связи
        for org_id in organization_ids:
            specialist_org = SpecialistOrganization(
                specialist_id=db_specialist.id,
                organization_id=org_id,
            )
            session.add(specialist_org)

    session.add(db_specialist)
    session.commit()
    session.refresh(db_specialist)
    return db_specialist


def delete_specialist(
    *,
    session: Session,
    specialist_id: UUID,
) -> None:
    """Удаление специалиста"""
    specialist = session.get(Specialist, specialist_id)
    if not specialist:
        raise HTTPException(
            status_code=404,
            detail="Specialist not found",
        )

    # Проверяем, есть ли обращения, где специалист является ответственным
    if specialist.responsible_appeals:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete specialist who is responsible for appeals",
        )

    # Удаляем связи с организациями
    statement = select(SpecialistOrganization).where(
        SpecialistOrganization.specialist_id == specialist_id
    )
    links = session.exec(statement).all()
    for link in links:
        session.delete(link)

    session.delete(specialist)
    session.commit()
