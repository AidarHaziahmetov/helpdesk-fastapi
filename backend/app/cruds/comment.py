from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

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
