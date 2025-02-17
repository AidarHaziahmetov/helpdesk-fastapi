from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.task import Task, TaskBase


def create_task(
    *,
    session: Session,
    task_in: TaskBase,
    appeal_id: UUID,
    user_id: UUID,
    description: str = "",
) -> Task:
    """Создание задачи"""
    db_task = Task(
        **task_in.model_dump(),
        appeal_id=appeal_id,
        user_id=user_id,
        description=description,
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_task(
    *,
    session: Session,
    task_id: UUID,
) -> Task | None:
    """Получение задачи по ID"""
    return session.get(Task, task_id)


def get_tasks(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    """Получение списка задач"""
    statement = select(Task).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_appeal_tasks(
    *,
    session: Session,
    appeal_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    """Получение списка задач обращения"""
    statement = (
        select(Task).where(Task.appeal_id == appeal_id).offset(skip).limit(limit)
    )
    return session.exec(statement).all()


def get_user_tasks(
    *,
    session: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    """Получение списка задач пользователя"""
    statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    return session.exec(statement).all()


def update_task(
    *,
    session: Session,
    db_task: Task,
    gitlab_url: str | None = None,
    status: str | None = None,
    description: str | None = None,
) -> Task:
    """Обновление задачи"""
    if gitlab_url is not None:
        db_task.gitlab_url = gitlab_url
    if status is not None:
        db_task.status = status
    if description is not None:
        db_task.description = description

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def delete_task(
    *,
    session: Session,
    task_id: UUID,
) -> None:
    """Удаление задачи"""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()
