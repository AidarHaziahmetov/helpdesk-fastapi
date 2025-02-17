from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.contract import Contract, ContractCreate, ContractUpdate
from app.models.priority import ContractStandardPriority


def create_contract(
    *,
    session: Session,
    contract_in: ContractCreate,
    standard_priority_ids: list[UUID] | None = None,
) -> Contract:
    """Создание контракта"""
    # Проверяем, что дата начала меньше даты окончания
    if contract_in.start_dt >= contract_in.end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    db_contract = Contract.model_validate(contract_in)
    session.add(db_contract)
    session.commit()
    session.refresh(db_contract)

    # Добавляем стандартные приоритеты
    if standard_priority_ids:
        for priority_id in standard_priority_ids:
            contract_priority = ContractStandardPriority(
                contract_id=db_contract.id,
                priority_id=priority_id,
            )
            session.add(contract_priority)
        session.commit()
        session.refresh(db_contract)

    return db_contract


def get_contract(
    *,
    session: Session,
    contract_id: UUID,
) -> Contract | None:
    """Получение контракта по ID"""
    return session.get(Contract, contract_id)


def get_contracts(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Contract]:
    """Получение списка контрактов"""
    statement = select(Contract).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_organization_contracts(
    *,
    session: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Contract]:
    """Получение списка контрактов организации"""
    statement = (
        select(Contract)
        .where(Contract.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_actual_organization_contract(
    *,
    session: Session,
    organization_id: UUID,
) -> Contract | None:
    """Получение актуального контракта организации"""
    statement = (
        select(Contract)
        .where(
            Contract.organization_id == organization_id,
            Contract.is_actual == True,  # noqa: E712
        )
        .order_by(Contract.end_dt.desc())
    )
    return session.exec(statement).first()


def update_contract(
    *,
    session: Session,
    db_contract: Contract,
    contract_in: ContractUpdate,
    standard_priority_ids: list[UUID] | None = None,
) -> Contract:
    """Обновление контракта"""
    # Проверяем даты, если они обновляются
    start_dt = contract_in.start_dt or db_contract.start_dt
    end_dt = contract_in.end_dt or db_contract.end_dt
    if start_dt >= end_dt:
        raise HTTPException(
            status_code=400,
            detail="Start date must be before end date",
        )

    update_data = contract_in.model_dump(exclude_unset=True)
    db_contract.sqlmodel_update(update_data)

    # Обновляем стандартные приоритеты
    if standard_priority_ids is not None:
        # Удаляем старые связи
        statement = select(ContractStandardPriority).where(
            ContractStandardPriority.contract_id == db_contract.id
        )
        existing_links = session.exec(statement).all()
        for link in existing_links:
            session.delete(link)

        # Добавляем новые связи
        for priority_id in standard_priority_ids:
            contract_priority = ContractStandardPriority(
                contract_id=db_contract.id,
                priority_id=priority_id,
            )
            session.add(contract_priority)

    session.add(db_contract)
    session.commit()
    session.refresh(db_contract)
    return db_contract


def delete_contract(
    *,
    session: Session,
    contract_id: UUID,
) -> None:
    """Удаление контракта"""
    contract = session.get(Contract, contract_id)
    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )

    # Проверяем, есть ли индивидуальные приоритеты
    if contract.individual_priorities:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete contract with individual priorities",
        )

    # Удаляем связи со стандартными приоритетами
    statement = select(ContractStandardPriority).where(
        ContractStandardPriority.contract_id == contract_id
    )
    links = session.exec(statement).all()
    for link in links:
        session.delete(link)

    session.delete(contract)
    session.commit()
