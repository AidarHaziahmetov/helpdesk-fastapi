from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.files import save_upload_file
from app.models.comment import Comment, CommentBase
from app.models.comment_file import CommentFile


def create_comment(
    *,
    session: Session,
    user_id: UUID,
    appeal_id: UUID,
    comment_in: CommentBase,
    files: list[UploadFile] | None = None,
) -> Comment:
    """Создание комментария"""
    db_comment = Comment(
        **comment_in.model_dump(),
        user_id=user_id,
        appeal_id=appeal_id,
        created_at=datetime.utcnow(),
    )
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)

    # Сохраняем файлы, если они есть
    if files:
        for file in files:
            # Сохраняем файл и получаем путь
            file_path = save_upload_file(
                file=file,
                folder="comment",
                entity_id=db_comment.id,
            )

            # Создаем запись в БД
            comment_file = CommentFile(
                comment_id=db_comment.id,
                file=file_path,
            )
            session.add(comment_file)

        session.commit()
        session.refresh(db_comment)

    return db_comment


def get_comment(
    *,
    session: Session,
    comment_id: UUID,
) -> Comment | None:
    """Получение комментария по ID"""
    return session.get(Comment, comment_id)


def get_appeal_comments(
    *,
    session: Session,
    appeal_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Comment]:
    """Получение комментариев обращения"""
    statement = (
        select(Comment)
        .where(Comment.appeal_id == appeal_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def update_comment(
    *,
    session: Session,
    db_comment: Comment,
    text: str,
) -> Comment:
    """Обновление комментария"""
    db_comment.text = text
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


def delete_comment(
    *,
    session: Session,
    comment_id: UUID,
) -> None:
    """Удаление комментария"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Удаляем файлы комментария
    for comment_file in comment.comment_files:
        session.delete(comment_file)

    session.delete(comment)
    session.commit()


def get_comment_file(
    *,
    session: Session,
    comment_id: UUID,
    file_id: UUID,
) -> CommentFile | None:
    """Получение файла комментария"""
    statement = select(CommentFile).where(
        CommentFile.comment_id == comment_id,
        CommentFile.id == file_id,
    )
    return session.exec(statement).first()


def add_comment_files(
    *,
    session: Session,
    comment_id: UUID,
    files: list[UploadFile],
) -> Comment:
    """Добавление файлов к существующему комментарию"""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Сохраняем новые файлы
    for file in files:
        # Сохраняем файл и получаем путь
        file_path = save_upload_file(
            file=file,
            folder="comment",
            entity_id=comment.id,
        )

        # Создаем запись в БД
        comment_file = CommentFile(
            comment_id=comment.id,
            file=file_path,
        )
        session.add(comment_file)

    session.commit()
    session.refresh(comment)
    return comment


async def create_comment_async(
    *,
    session: AsyncSession,
    user_id: UUID,
    appeal_id: UUID,
    comment_in: CommentBase,
    files: list[UploadFile] | None = None,
) -> Comment:
    """Асинхронное создание комментария"""
    db_comment = Comment(
        **comment_in.model_dump(),
        user_id=user_id,
        appeal_id=appeal_id,
        created_at=datetime.utcnow(),
    )
    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    # Сохраняем файлы, если они есть
    if files:
        for file in files:
            # Сохраняем файл и получаем путь
            file_path = await save_upload_file_async(
                file=file,
                folder="comment",
                entity_id=db_comment.id,
            )

            # Создаем запись в БД
            comment_file = CommentFile(
                comment_id=db_comment.id,
                file=file_path,
            )
            session.add(comment_file)

        await session.commit()
        await session.refresh(db_comment)

    return db_comment


async def get_comment_async(
    *,
    session: AsyncSession,
    comment_id: UUID,
) -> Comment | None:
    """Асинхронное получение комментария по ID"""
    return await session.get(Comment, comment_id)


async def get_appeal_comments_async(
    *,
    session: AsyncSession,
    appeal_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[Comment]:
    """Асинхронное получение комментариев обращения"""
    statement = (
        select(Comment)
        .where(Comment.appeal_id == appeal_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def update_comment_async(
    *,
    session: AsyncSession,
    db_comment: Comment,
    text: str,
) -> Comment:
    """Асинхронное обновление комментария"""
    db_comment.text = text
    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)
    return db_comment


async def delete_comment_async(
    *,
    session: AsyncSession,
    comment_id: UUID,
) -> None:
    """Асинхронное удаление комментария"""
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Удаляем файлы комментария
    for comment_file in comment.comment_files:
        await session.delete(comment_file)

    await session.delete(comment)
    await session.commit()


async def get_comment_file_async(
    *,
    session: AsyncSession,
    comment_id: UUID,
    file_id: UUID,
) -> CommentFile | None:
    """Асинхронное получение файла комментария"""
    statement = select(CommentFile).where(
        CommentFile.comment_id == comment_id,
        CommentFile.id == file_id,
    )
    result = await session.exec(statement)
    return result.first()


async def add_comment_files_async(
    *,
    session: AsyncSession,
    comment_id: UUID,
    files: list[UploadFile],
) -> Comment:
    """Асинхронное добавление файлов к существующему комментарию"""
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    # Сохраняем новые файлы
    for file in files:
        # Сохраняем файл и получаем путь
        file_path = await save_upload_file_async(
            file=file,
            folder="comment",
            entity_id=comment.id,
        )

        # Создаем запись в БД
        comment_file = CommentFile(
            comment_id=comment.id,
            file=file_path,
        )
        session.add(comment_file)

    await session.commit()
    await session.refresh(comment)
    return comment


async def save_upload_file_async(
    *,
    file: UploadFile,
    folder: str,
    entity_id: UUID,
) -> str:
    """Асинхронное сохранение загруженного файла"""
    # Здесь должна быть асинхронная реализация сохранения файла
    # Для простоты используем синхронную версию
    return save_upload_file(file=file, folder=folder, entity_id=entity_id)
