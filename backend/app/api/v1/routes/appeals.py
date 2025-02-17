from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.v1.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.files import get_file_response, save_upload_file
from app.cruds import appeal as appeal_crud
from app.models.appeal import Appeal, AppealBase
from app.models.appeal_file import AppealFile
from app.utils.bot import send_appeal_updated_message, send_new_appeal_message
from app.utils.email import send_new_appeal_email, send_new_status_email

router = APIRouter(prefix="/appeals", tags=["appeals"])


@router.get("/", response_model=list[Appeal])
def get_appeals(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Получить список обращений"""
    appeals = appeal_crud.get_appeals(
        session=session, user=current_user, skip=skip, limit=limit
    )
    return appeals


@router.get("/{appeal_id}", response_model=Appeal)
def get_appeal(
    appeal_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Получить обращение по ID"""
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверка прав доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

    return appeal


@router.post("/", response_model=Appeal)
def create_appeal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_in: AppealBase,
    # files: list[UploadFile] = File(None),
) -> Any:
    """Создать новое обращение

    - **files**: Опциональные файлы для загрузки
    """
    # try:
    #     appeal_data = json.loads(appeal_in)
    #     appeal_in = AppealBase(**appeal_data)
    # except json.JSONDecodeError:
    #     raise HTTPException(status_code=422, detail="Invalid JSON format in appeal_in")
    # except ValueError as e:
    #     raise HTTPException(status_code=422, detail=f"Invalid appeal data: {str(e)}")

    if not hasattr(current_user, "representative"):
        raise HTTPException(
            status_code=403, detail="Only representatives can create appeals"
        )

    appeal = appeal_crud.create_appeal(
        session=session,
        user=current_user,
        appeal=appeal_in,  # , files=files
    )

    # Отправка уведомлений
    send_new_appeal_email(appeal)
    send_new_appeal_message(appeal)

    return appeal


@router.patch("/{appeal_id}", response_model=Appeal)
def update_appeal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_id: UUID,
    status_id: UUID | None = None,
    responsible_user_id: UUID | None = None,
    solving: str | None = None,
) -> Any:
    """Обновить обращение"""
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверка прав на обновление
    if not (current_user.is_superuser or appeal.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    old_status = appeal.status_id
    updated_appeal = appeal_crud.update_appeal(
        session=session,
        db_appeal=appeal,
        status_id=status_id,
        responsible_user_id=responsible_user_id,
        solving=solving,
    )

    if status_id and status_id != old_status:
        send_new_status_email(updated_appeal)
        send_appeal_updated_message(updated_appeal)

    return updated_appeal


@router.get("/{appeal_id}/files/{file_id}")
def get_appeal_file(
    appeal_id: UUID,
    file_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> FileResponse:
    """Получить файл обращения"""
    # Проверяем существование обращения
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

    # Получаем файл
    appeal_file = session.get(AppealFile, file_id)
    if not appeal_file or appeal_file.appeal_id != appeal_id:
        raise HTTPException(status_code=404, detail="File not found")

    return get_file_response(file_path=appeal_file.file)


@router.post("/{appeal_id}/files")
def upload_appeal_files(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_id: UUID,
    files: list[UploadFile] = File(default=..., description="Файлы для загрузки"),
) -> list[AppealFile]:
    """Загрузить файлы для обращения

    - **files**: Один или несколько файлов для загрузки
    """
    # Проверяем существование обращения
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

    appeal_files = []
    for file in files:
        # Проверяем размер файла
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes",
            )

        # Сохраняем файл
        file_path = save_upload_file(
            file=file,
            folder="appeal",
            entity_id=appeal_id,
        )

        # Создаем запись в БД
        appeal_file = AppealFile(
            appeal_id=appeal_id,
            file=file_path,
        )
        session.add(appeal_file)
        appeal_files.append(appeal_file)

    session.commit()
    for file in appeal_files:
        session.refresh(file)

    return appeal_files


@router.delete("/{appeal_id}/files/{file_id}")
def delete_appeal_file(
    appeal_id: UUID,
    file_id: UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Удалить файл обращения"""
    # Проверяем существование обращения
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

    # Получаем файл
    appeal_file = session.get(AppealFile, file_id)
    if not appeal_file or appeal_file.appeal_id != appeal_id:
        raise HTTPException(status_code=404, detail="File not found")

    # Удаляем физический файл
    file_path = Path(settings.UPLOAD_DIR) / appeal_file.file
    if file_path.exists():
        file_path.unlink()

    # Удаляем запись из БД
    session.delete(appeal_file)
    session.commit()


@router.delete("/{appeal_id}")
def delete_appeal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    appeal_id: UUID,
) -> None:
    """
    Удалить обращение

    Только суперпользователи или создатель обращения могут его удалить.
    При удалении также удаляются все связанные файлы.
    """
    # Проверяем существование обращения
    appeal = appeal_crud.get_appeal(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not (current_user.is_superuser or appeal.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Удаляем физические файлы
    for appeal_file in appeal.files:
        file_path = Path(settings.UPLOAD_DIR) / appeal_file.file
        if file_path.exists():
            file_path.unlink()

    # Удаляем обращение (каскадно удалятся все связанные записи)
    session.delete(appeal)
    session.commit()
