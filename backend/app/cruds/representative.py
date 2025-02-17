from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.representative import Representative, RepresentativeBase


def create_representative(
    *,
    session: Session,
    representative_in: RepresentativeBase,
    user_id: UUID,
    organization_id: UUID,
    main_representative_id: UUID | None = None,
) -> Representative:
    """Создание представителя организации"""
    db_representative = Representative(
        **representative_in.model_dump(),
        user_id=user_id,
        organization_id=organization_id,
        main_representative_id=main_representative_id,
    )
    session.add(db_representative)
    session.commit()
    session.refresh(db_representative)
    return db_representative


def get_representative(
    *,
    session: Session,
    representative_id: UUID,
) -> Representative | None:
    """Получение представителя по ID"""
    return session.get(Representative, representative_id)


def get_representative_by_user_id(
    *,
    session: Session,
    user_id: UUID,
) -> Representative | None:
    """Получение представителя по ID пользователя"""
    statement = select(Representative).where(Representative.user_id == user_id)
    return session.exec(statement).first()


def get_representatives(
    *,
    session: Session,
    organization_id: UUID | None = None,
    main_representative_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Representative]:
    """Получение списка представителей с фильтрацией"""
    statement = select(Representative)

    if organization_id:
        statement = statement.where(Representative.organization_id == organization_id)
    if main_representative_id:
        statement = statement.where(
            Representative.main_representative_id == main_representative_id
        )

    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def update_representative(
    *,
    session: Session,
    db_representative: Representative,
    representative_in: RepresentativeBase,
) -> Representative:
    """Обновление данных представителя"""
    representative_data = representative_in.model_dump(exclude_unset=True)
    db_representative.sqlmodel_update(representative_data)
    session.add(db_representative)
    session.commit()
    session.refresh(db_representative)
    return db_representative


def delete_representative(
    *,
    session: Session,
    representative_id: UUID,
) -> None:
    """Удаление представителя"""
    representative = session.get(Representative, representative_id)
    if not representative:
        raise HTTPException(
            status_code=404,
            detail="Representative not found",
        )

    # Проверяем, есть ли подчиненные представители
    if representative.representatives:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete representative with subordinate representatives",
        )

    session.delete(representative)
    session.commit()


def get_organization_representatives(
    *,
    session: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Representative]:
    """Получение всех представителей организации"""
    statement = (
        select(Representative)
        .where(Representative.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_subordinate_representatives(
    *,
    session: Session,
    main_representative_id: UUID,
) -> list[Representative]:
    """Получение списка подчиненных представителей"""
    statement = select(Representative).where(
        Representative.main_representative_id == main_representative_id
    )
    return session.exec(statement).all()
