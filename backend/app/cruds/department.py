from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.department import Department, DepartmentCreate, DepartmentUpdate


def create_department(
    *,
    session: Session,
    department_in: DepartmentCreate,
) -> Department:
    """Создание отдела"""
    # Проверяем уникальность имени в рамках организации
    existing_department = get_department_by_name_and_organization(
        session=session,
        name=department_in.name,
        organization_id=department_in.organization_id,
    )
    if existing_department:
        raise HTTPException(
            status_code=400,
            detail="Department with this name already exists in the organization",
        )

    db_department = Department.model_validate(department_in)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


def get_department(
    *,
    session: Session,
    department_id: UUID,
) -> Department | None:
    """Получение отдела по ID"""
    return session.get(Department, department_id)


def get_departments(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Department]:
    """Получение списка отделов"""
    statement = select(Department).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_organization_departments(
    *,
    session: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Department]:
    """Получение списка отделов организации"""
    statement = (
        select(Department)
        .where(Department.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_department_by_name_and_organization(
    *,
    session: Session,
    name: str,
    organization_id: UUID,
) -> Department | None:
    """Получение отдела по имени и организации"""
    statement = select(Department).where(
        Department.name == name,
        Department.organization_id == organization_id,
    )
    return session.exec(statement).first()


def update_department(
    *,
    session: Session,
    db_department: Department,
    department_in: DepartmentUpdate,
) -> Department:
    """Обновление отдела"""
    # Проверяем уникальность имени в рамках организации
    if department_in.name and department_in.name != db_department.name:
        existing_department = get_department_by_name_and_organization(
            session=session,
            name=department_in.name,
            organization_id=db_department.organization_id,
        )
        if existing_department:
            raise HTTPException(
                status_code=400,
                detail="Department with this name already exists in the organization",
            )

    update_data = department_in.model_dump(exclude_unset=True)
    db_department.sqlmodel_update(update_data)
    session.add(db_department)
    session.commit()
    session.refresh(db_department)
    return db_department


def delete_department(
    *,
    session: Session,
    department_id: UUID,
) -> None:
    """Удаление отдела"""
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    # Проверяем, есть ли специалисты в отделе
    if department.specialists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete department with specialists",
        )

    session.delete(department)
    session.commit()
