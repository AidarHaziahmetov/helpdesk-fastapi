import os
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.status import HTTP_404_NOT_FOUND

from app.core.config import settings


def save_upload_file(
    *,
    file: UploadFile,
    folder: str,
    entity_id: UUID,
) -> str:
    """
    Сохраняет загруженный файл и возвращает путь к нему

    Args:
        file: Загруженный файл
        folder: Папка для сохранения (например, 'appeal' или 'comment')
        entity_id: ID сущности, к которой относится файл
    """
    # Создаем директорию если её нет
    upload_dir = Path(settings.UPLOAD_DIR) / folder / str(entity_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем файл с оригинальным именем
    file_path = upload_dir / file.filename

    with open(file_path, "wb") as buffer:
        # Копируем содержимое файла
        buffer.write(file.file.read())

    # Возвращаем относительный путь для сохранения в БД
    return os.path.join(folder, str(entity_id), file.filename)


def get_file_response(*, file_path: str) -> FileResponse:
    """
    Создает FileResponse для загруженного файла

    Args:
        file_path: Относительный путь к файлу (как сохранен в БД)
    """
    full_path = Path(settings.UPLOAD_DIR) / file_path

    if not full_path.exists():
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(
        path=full_path,
        filename=full_path.name,  # Оригинальное имя файла для скачивания
        media_type=None,  # Автоопределение типа файла
    )
