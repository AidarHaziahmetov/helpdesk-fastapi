from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.deps import SessionDep, get_current_user
from app.cruds.task import (
    create_task,
    delete_task,
    get_appeal_tasks,
    get_task,
    get_tasks,
    get_user_tasks,
    update_task,
)
from app.models.task import Task, TaskBase
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Task)
def create(
    *,
    session: SessionDep,
    task_in: TaskBase,
    appeal_id: UUID,
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    Создание новой задачи.
    """
    return create_task(
        session=session,
        task_in=task_in,
        appeal_id=appeal_id,
        user_id=current_user.id,
    )


@router.get("/{task_id}", response_model=Task)
def get_by_id(
    *,
    session: SessionDep,
    task_id: UUID,
    _: User = Depends(get_current_user),
) -> Task:
    """
    Получение задачи по ID.
    """
    db_task = get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )
    return db_task


@router.get("/", response_model=list[Task])
def get_list(
    *,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_user),
) -> list[Task]:
    """
    Получение списка всех задач.
    """
    return get_tasks(session=session, skip=skip, limit=limit)


@router.get("/appeal/{appeal_id}", response_model=list[Task])
def get_by_appeal(
    *,
    session: SessionDep,
    appeal_id: UUID,
    skip: int = 0,
    limit: int = 100,
    _: User = Depends(get_current_user),
) -> list[Task]:
    """
    Получение списка задач обращения.
    """
    return get_appeal_tasks(
        session=session,
        appeal_id=appeal_id,
        skip=skip,
        limit=limit,
    )


@router.get("/user/{user_id}", response_model=list[Task])
def get_by_user(
    *,
    session: SessionDep,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    """
    Получение списка задач пользователя.
    Пользователь может получить только свои задачи.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to get other user's tasks",
        )
    return get_user_tasks(
        session=session,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.patch("/{task_id}", response_model=Task)
def update(
    *,
    session: SessionDep,
    task_id: UUID,
    gitlab_url: str | None = None,
    status: str | None = None,
    description: str | None = None,
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    Обновление задачи.
    Пользователь может обновлять только свои задачи.
    """
    db_task = get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update this task",
        )
    return update_task(
        session=session,
        db_task=db_task,
        gitlab_url=gitlab_url,
        status=status,
        description=description,
    )


@router.delete("/{task_id}")
def delete(
    *,
    session: SessionDep,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Удаление задачи.
    Пользователь может удалять только свои задачи.
    """
    db_task = get_task(session=session, task_id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to delete this task",
        )
    delete_task(session=session, task_id=task_id)
