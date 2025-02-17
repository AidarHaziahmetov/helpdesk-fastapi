from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.project import (
    OrganizationProject,
    Project,
    ProjectBase,
)


def create_project(
    *,
    session: Session,
    project_in: ProjectBase,
    organization_ids: list[UUID] | None = None,
) -> Project:
    """Создание проекта"""
    # Проверяем уникальность имени
    existing_project = get_project_by_name(session=session, name=project_in.name)
    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project with this name already exists",
        )

    db_project = Project.model_validate(project_in)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    # Добавляем связи с организациями
    if organization_ids:
        for org_id in organization_ids:
            project_org = OrganizationProject(
                project_id=db_project.id,
                organization_id=org_id,
            )
            session.add(project_org)
        session.commit()
        session.refresh(db_project)

    return db_project


def get_project(
    *,
    session: Session,
    project_id: UUID,
) -> Project | None:
    """Получение проекта по ID"""
    return session.get(Project, project_id)


def get_projects(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Project]:
    """Получение списка проектов"""
    statement = select(Project).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_organization_projects(
    *,
    session: Session,
    organization_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Project]:
    """Получение списка проектов организации"""
    statement = (
        select(Project)
        .join(OrganizationProject)
        .where(OrganizationProject.organization_id == organization_id)
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_project_by_name(
    *,
    session: Session,
    name: str,
) -> Project | None:
    """Получение проекта по имени"""
    statement = select(Project).where(Project.name == name)
    return session.exec(statement).first()


def update_project(
    *,
    session: Session,
    db_project: Project,
    project_in: ProjectBase,
    organization_ids: list[UUID] | None = None,
) -> Project:
    """Обновление проекта"""
    # Проверяем уникальность имени
    if project_in.name != db_project.name:
        existing_project = get_project_by_name(session=session, name=project_in.name)
        if existing_project:
            raise HTTPException(
                status_code=400,
                detail="Project with this name already exists",
            )

    update_data = project_in.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(update_data)

    # Обновляем связи с организациями
    if organization_ids is not None:
        # Удаляем старые связи
        statement = select(OrganizationProject).where(
            OrganizationProject.project_id == db_project.id
        )
        existing_links = session.exec(statement).all()
        for link in existing_links:
            session.delete(link)

        # Добавляем новые связи
        for org_id in organization_ids:
            project_org = OrganizationProject(
                project_id=db_project.id,
                organization_id=org_id,
            )
            session.add(project_org)

    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


def delete_project(
    *,
    session: Session,
    project_id: UUID,
) -> None:
    """Удаление проекта"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    # Удаляем связи с организациями
    statement = select(OrganizationProject).where(
        OrganizationProject.project_id == project_id
    )
    links = session.exec(statement).all()
    for link in links:
        session.delete(link)

    session.delete(project)
    session.commit()
