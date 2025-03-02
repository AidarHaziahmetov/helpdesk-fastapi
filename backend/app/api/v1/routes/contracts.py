from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import SessionDep, get_current_user
from app.cruds.contract import (
    create_contract,
    delete_contract,
    get_actual_organization_contract,
    get_contract,
    get_contracts,
    get_organization_contracts,
    update_contract,
)
from app.models.contract import Contract, ContractCreate, ContractUpdate
from app.models.user import User

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/", response_model=Contract)
def create(
    *,
    session: SessionDep,
    contract_in: ContractCreate,
    _: User = Depends(get_current_user),
) -> Contract:
    """
    Создание нового контракта.
    """
    return create_contract(session=session, contract_in=contract_in)


@router.get("/{contract_id}", response_model=Contract)
def get_by_id(
    *,
    session: SessionDep,
    contract_id: UUID,
    _: User = Depends(get_current_user),
) -> Contract:
    """
    Получение контракта по ID.
    """
    db_contract = get_contract(session=session, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )
    return db_contract


@router.get("/", response_model=list[Contract])
def get_list(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_user),
) -> list[Contract]:
    """
    Получение списка всех контрактов.
    """
    return get_contracts(session=session, skip=skip, limit=limit)


@router.get("/organization/{organization_id}", response_model=list[Contract])
def get_by_organization(
    *,
    session: SessionDep,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_user),
) -> list[Contract]:
    """
    Получение списка контрактов организации.
    """
    return get_organization_contracts(
        session=session,
        organization_id=organization_id,
        skip=skip,
        limit=limit,
    )


@router.get("/organization/{organization_id}/actual", response_model=Contract)
def get_actual(
    *,
    session: SessionDep,
    organization_id: UUID,
    current_date: date | None = None,
    _: User = Depends(get_current_user),
) -> Contract:
    """
    Получение актуального контракта организации.
    """
    db_contract = get_actual_organization_contract(
        session=session,
        organization_id=organization_id,
        current_date=current_date or date.today(),
    )
    if not db_contract:
        raise HTTPException(
            status_code=404,
            detail="No active contract found for this organization",
        )
    return db_contract


@router.patch("/{contract_id}", response_model=Contract)
def update(
    *,
    session: SessionDep,
    contract_id: UUID,
    contract_in: ContractUpdate,
    _: User = Depends(get_current_user),
) -> Contract:
    """
    Обновление контракта.
    """
    db_contract = get_contract(session=session, contract_id=contract_id)
    if not db_contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )
    return update_contract(
        session=session,
        db_contract=db_contract,
        contract_in=contract_in,
    )


@router.delete("/{contract_id}")
def delete(
    *,
    session: SessionDep,
    contract_id: UUID,
    _: User = Depends(get_current_user),
) -> None:
    """
    Удаление контракта.
    """
    delete_contract(session=session, contract_id=contract_id)
