from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.priority import (
    BasePriorityBase,
    ContractStandardPriority,
    IndividualPriority,
    StandardPriority,
)


def create_standard_priority(
    *,
    session: Session,
    priority_in: BasePriorityBase,
) -> StandardPriority:
    """Создание стандартного приоритета"""
    # Проверяем уникальность имени
    existing_priority = get_standard_priority_by_name(
        session=session, name=priority_in.name
    )
    if existing_priority:
        raise HTTPException(
            status_code=400,
            detail="Priority with this name already exists",
        )

    db_priority = StandardPriority.model_validate(priority_in)
    session.add(db_priority)
    session.commit()
    session.refresh(db_priority)
    return db_priority


def create_individual_priority(
    *,
    session: Session,
    priority_in: BasePriorityBase,
    contract_id: UUID,
) -> IndividualPriority:
    """Создание индивидуального приоритета"""
    # Проверяем уникальность имени в рамках контракта
    existing_priority = get_individual_priority_by_name_and_contract(
        session=session, name=priority_in.name, contract_id=contract_id
    )
    if existing_priority:
        raise HTTPException(
            status_code=400,
            detail="Priority with this name already exists in this contract",
        )

    db_priority = IndividualPriority(
        **priority_in.model_dump(),
        contract_id=contract_id,
    )
    session.add(db_priority)
    session.commit()
    session.refresh(db_priority)
    return db_priority


def get_standard_priority(
    *,
    session: Session,
    priority_id: UUID,
) -> StandardPriority | None:
    """Получение стандартного приоритета по ID"""
    return session.get(StandardPriority, priority_id)


def get_individual_priority(
    *,
    session: Session,
    priority_id: UUID,
) -> IndividualPriority | None:
    """Получение индивидуального приоритета по ID"""
    return session.get(IndividualPriority, priority_id)


def get_standard_priorities(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[StandardPriority]:
    """Получение списка стандартных приоритетов"""
    statement = select(StandardPriority).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_contract_individual_priorities(
    *,
    session: Session,
    contract_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[IndividualPriority]:
    """Получение списка индивидуальных приоритетов контракта"""
    statement = (
        select(IndividualPriority)
        .where(IndividualPriority.contract_id == contract_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_standard_priority_by_name(
    *,
    session: Session,
    name: str,
) -> StandardPriority | None:
    """Получение стандартного приоритета по имени"""
    statement = select(StandardPriority).where(StandardPriority.name == name)
    return session.exec(statement).first()


def get_individual_priority_by_name_and_contract(
    *,
    session: Session,
    name: str,
    contract_id: UUID,
) -> IndividualPriority | None:
    """Получение индивидуального приоритета по имени и контракту"""
    statement = select(IndividualPriority).where(
        IndividualPriority.name == name,
        IndividualPriority.contract_id == contract_id,
    )
    return session.exec(statement).first()


def update_standard_priority(
    *,
    session: Session,
    db_priority: StandardPriority,
    priority_in: BasePriorityBase,
) -> StandardPriority:
    """Обновление стандартного приоритета"""
    if priority_in.name != db_priority.name:
        existing_priority = get_standard_priority_by_name(
            session=session, name=priority_in.name
        )
        if existing_priority:
            raise HTTPException(
                status_code=400,
                detail="Priority with this name already exists",
            )

    update_data = priority_in.model_dump(exclude_unset=True)
    db_priority.sqlmodel_update(update_data)
    session.add(db_priority)
    session.commit()
    session.refresh(db_priority)
    return db_priority


def update_individual_priority(
    *,
    session: Session,
    db_priority: IndividualPriority,
    priority_in: BasePriorityBase,
) -> IndividualPriority:
    """Обновление индивидуального приоритета"""
    if priority_in.name != db_priority.name:
        existing_priority = get_individual_priority_by_name_and_contract(
            session=session,
            name=priority_in.name,
            contract_id=db_priority.contract_id,
        )
        if existing_priority:
            raise HTTPException(
                status_code=400,
                detail="Priority with this name already exists in this contract",
            )

    update_data = priority_in.model_dump(exclude_unset=True)
    db_priority.sqlmodel_update(update_data)
    session.add(db_priority)
    session.commit()
    session.refresh(db_priority)
    return db_priority


def delete_standard_priority(
    *,
    session: Session,
    priority_id: UUID,
) -> None:
    """Удаление стандартного приоритета"""
    priority = session.get(StandardPriority, priority_id)
    if not priority:
        raise HTTPException(
            status_code=404,
            detail="Priority not found",
        )

    # Удаляем связи с контрактами
    statement = select(ContractStandardPriority).where(
        ContractStandardPriority.priority_id == priority_id
    )
    links = session.exec(statement).all()
    for link in links:
        session.delete(link)

    session.delete(priority)
    session.commit()


def delete_individual_priority(
    *,
    session: Session,
    priority_id: UUID,
) -> None:
    """Удаление индивидуального приоритета"""
    priority = session.get(IndividualPriority, priority_id)
    if not priority:
        raise HTTPException(
            status_code=404,
            detail="Priority not found",
        )

    session.delete(priority)
    session.commit()
