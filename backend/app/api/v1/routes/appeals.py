from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.api.v1.deps import AsyncSessionDep, CurrentUserAsync
from app.core.config import settings
from app.core.files import get_file_response, save_upload_file
from app.cruds.appeal import (
    create_appeal_async,
    delete_appeal_async,
    get_appeal_async,
    get_appeals_async,
    update_appeal_async,
)
from app.models.appeal import Appeal, AppealBase
from app.models.appeal_file import AppealFile
from app.models.common import Message
from app.utils.bot import send_appeal_updated_message, send_new_appeal_message
from app.utils.email import send_new_appeal_email, send_new_status_email

router = APIRouter(prefix="/appeals", tags=["appeals"])


@router.get("/", response_model=list[Appeal])
async def read_appeals(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить список обращений.

    - Обычные пользователи видят только свои обращения
    - Представители организаций видят обращения своей организации
    - Суперпользователи видят все обращения
    """
    appeals = await get_appeals_async(
        session=session, user=current_user, skip=skip, limit=limit
    )
    return appeals


@router.get("/{appeal_id}", response_model=Appeal)
async def get_appeal(
    appeal_id: UUID,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
) -> Any:
    """Получить обращение по ID"""
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверка прав доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    return appeal


@router.post("/", response_model=Appeal)
async def create_new_appeal(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_in: str = Form(...),
    # files: list[UploadFile] = File(None),
) -> Any:
    """
    Создать новое обращение.
    """
    # Добавлено: преобразование JSON-строки в объект AppealBase
    try:
        appeal_data = AppealBase.model_validate_json(appeal_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid appeal data") from e

    # Создаем обращение используя распарсенные данные
    appeal = await create_appeal_async(
        session=session,
        user=current_user,
        appeal=appeal_data,
    )

    # Отправляем уведомления
    try:
        await send_new_appeal_email(appeal=appeal)
    except Exception as e:
        # Логируем ошибку, но не прерываем выполнение
        print(f"Error sending email: {e}")

    try:
        await send_new_appeal_message(appeal=appeal)
    except Exception as e:
        # Логируем ошибку, но не прерываем выполнение
        print(f"Error sending message: {e}")

    # Загружаем файлы
    # if files:
    #     for file in files:
    #         await upload_appeal_files(
    #             session=session,
    #             current_user=current_user,
    #             appeal_id=appeal.id,
    #             file=file,
    #         )

    return appeal


@router.patch("/{appeal_id}", response_model=Appeal)
async def update_appeal(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_id: UUID,
    status_id: UUID | None = None,
    responsible_user_id: UUID | None = None,
    solving: str | None = None,
) -> Any:
    """Обновить обращение"""
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверка прав на обновление
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    old_status = appeal.status_id
    updated_appeal = await update_appeal_async(
        session=session,
        db_appeal=appeal,
        appeal_in=AppealBase(
            status_id=status_id,
            responsible_user_id=responsible_user_id,
            solving=solving,
        ),
    )

    if status_id and status_id != old_status:
        await send_new_status_email(updated_appeal)
        await send_appeal_updated_message(updated_appeal)

    return updated_appeal


@router.get("/{appeal_id}/files/{file_id}")
async def get_appeal_file(
    appeal_id: UUID,
    file_id: UUID,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
) -> Any:
    """Получить файл обращения"""
    # Проверяем существование обращения
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Получаем файл
    appeal_file = await session.get(AppealFile, file_id)
    if not appeal_file or appeal_file.appeal_id != appeal_id:
        raise HTTPException(status_code=404, detail="File not found")

    return await get_file_response(file_path=appeal_file.file)


@router.post("/{appeal_id}/files")
async def upload_appeal_files(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_id: UUID,
    files: list[UploadFile] = File(...),  # noqa: UP006
) -> list[AppealFile]:
    """Загрузить файлы для обращения

    - **files**: Один или несколько файлов для загрузки
    """
    # Проверяем существование обращения
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
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

    await session.commit()
    for file in appeal_files:
        await session.refresh(file)

    return appeal_files


@router.delete("/{appeal_id}/files/{file_id}")
async def delete_appeal_file(
    appeal_id: UUID,
    file_id: UUID,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
) -> None:
    """Удалить файл обращения"""
    # Проверяем существование обращения
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Получаем файл
    appeal_file = await session.get(AppealFile, file_id)
    if not appeal_file or appeal_file.appeal_id != appeal_id:
        raise HTTPException(status_code=404, detail="File not found")

    # Удаляем физический файл
    file_path = Path(settings.UPLOAD_DIR) / appeal_file.file
    if file_path.exists():
        file_path.unlink()

    # Удаляем запись из БД
    await session.delete(appeal_file)
    await session.commit()


@router.delete("/{appeal_id}")
async def delete_appeal(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_id: UUID,
) -> Message:
    """
    Удалить обращение

    Только суперпользователи или создатель обращения могут его удалить.
    При удалении также удаляются все связанные файлы.
    """
    # Проверяем существование обращения
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        if hasattr(current_user, "representative"):
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        elif appeal.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Удаляем физические файлы
    for appeal_file in appeal.files:
        file_path = Path(settings.UPLOAD_DIR) / appeal_file.file
        if file_path.exists():
            file_path.unlink()

    # Удаляем обращение (каскадно удалятся все связанные записи)
    await delete_appeal_async(session=session, appeal_id=appeal_id)
    return Message(message="Appeal deleted successfully")
