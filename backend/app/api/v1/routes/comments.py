from typing import Any
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.v1.deps import AsyncSessionDep, CurrentUserAsync
from app.core.files import get_file_response
from app.cruds.appeal import get_appeal_async
from app.cruds.comment import (
    create_comment_async,
    get_appeal_comments_async,
    get_comment_async,
    get_comment_file_async,
)
from app.models.comment import Comment, CommentBase

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/appeal/{appeal_id}", response_model=list[Comment])
async def read_appeal_comments(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получить комментарии к обращению.
    """
    # Проверка доступа к обращению
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        # Если пользователь - представитель организации
        if (
            hasattr(current_user, "representative")
            and appeal.organization_id != current_user.representative.organization_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to access this appeal's comments",
            )
        # Если обычный пользователь, проверяем что это его обращение
        elif appeal.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to access this appeal's comments",
            )

    comments = await get_appeal_comments_async(
        session=session, appeal_id=appeal_id, skip=skip, limit=limit
    )
    return comments


@router.post("/appeal/{appeal_id}", response_model=Comment)
async def create_new_comment(
    *,
    session: AsyncSessionDep,
    current_user: CurrentUserAsync,
    appeal_id: UUID,
    comment_in: CommentBase,
    files: list[UploadFile] = File(None),  # noqa: UP006
) -> Any:
    """
    Создать новый комментарий к обращению.
    """
    # Проверка доступа к обращению
    appeal = await get_appeal_async(session=session, appeal_id=appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="Appeal not found")

    # Проверяем права доступа
    if not current_user.is_superuser:
        # Если пользователь - представитель организации
        if hasattr(current_user, "representative"):
            # Проверяем, что обращение принадлежит организации представителя
            if appeal.organization_id != current_user.representative.organization_id:
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to comment on this appeal",
                )
        # Если обычный пользователь, проверяем что это его обращение
        elif appeal.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to comment on this appeal",
            )

    comment = await create_comment_async(
        session=session,
        user_id=current_user.id,
        appeal_id=appeal_id,
        comment_in=comment_in,
        files=files,
    )
    return comment


@router.get("/{comment_id}", response_model=Comment)
async def read_comment(
    *,
    session: AsyncSessionDep,
    _current_user: CurrentUserAsync,
    comment_id: UUID,
) -> Any:
    """
    Получить комментарий по ID.
    """
    comment = await get_comment_async(session=session, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Проверка доступа к комментарию
    appeal = await get_appeal_async(session=session, appeal_id=comment.appeal_id)

    # Проверяем права доступа
    if not _current_user.is_superuser:
        # Если пользователь - представитель организации
        if (
            hasattr(_current_user, "representative")
            and appeal.organization_id != _current_user.representative.organization_id
        ):
            raise HTTPException(
                status_code=403, detail="Not enough permissions to access this comment"
            )
        # Если обычный пользователь, проверяем что это его обращение
        elif appeal.user_id != _current_user.id:
            raise HTTPException(
                status_code=403, detail="Not enough permissions to access this comment"
            )

    return comment


# @router.patch("/{comment_id}", response_model=Comment)
# async def update_comment_text(
#     *,
#     session: AsyncSessionDep,
#     current_user: CurrentUserAsync,
#     comment_id: UUID,
#     text: str,
# ) -> Any:
#     """
#     Обновить текст комментария.
#     Пользователь может редактировать только свои комментарии.
#     """
#     comment = await get_comment_async(session=session, comment_id=comment_id)
#     if not comment:
#         raise HTTPException(status_code=404, detail="Comment not found")

#     if comment.user_id != current_user.id and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="Not enough permissions to update this comment"
#         )

#     updated_comment = await update_comment_async(
#         session=session, db_comment=comment, text=text
#     )
#     return updated_comment


# @router.delete("/{comment_id}", response_model=Message)
# async def delete_comment_by_id(
#     *,
#     session: AsyncSessionDep,
#     current_user: CurrentUserAsync,
#     comment_id: UUID,
# ) -> Any:
#     """
#     Удалить комментарий.
#     Пользователь может удалять только свои комментарии.
#     """
#     comment = await get_comment_async(session=session, comment_id=comment_id)
#     if not comment:
#         raise HTTPException(status_code=404, detail="Comment not found")

#     if comment.user_id != current_user.id and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="Not enough permissions to delete this comment"
#         )

#     await delete_comment_async(session=session, comment_id=comment_id)
#     return Message(message="Comment deleted successfully")


# @router.post("/{comment_id}/files", response_model=Comment)
# async def add_files_to_comment(
#     *,
#     session: AsyncSessionDep,
#     current_user: CurrentUserAsync,
#     comment_id: UUID,
#     files: List[UploadFile] = File(...),
# ) -> Any:
#     """
#     Добавить файлы к существующему комментарию.
#     Пользователь может добавлять файлы только к своим комментариям.
#     """
#     comment = await get_comment_async(session=session, comment_id=comment_id)
#     if not comment:
#         raise HTTPException(status_code=404, detail="Comment not found")

#     if comment.user_id != current_user.id and not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="Not enough permissions to update this comment"
#         )

#     # Проверяем размер файлов
#     for file in files:
#         if file.size > settings.MAX_UPLOAD_SIZE:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"File {file.filename} is too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes",
#             )

#     updated_comment = await add_comment_files_async(
#         session=session, comment_id=comment_id, files=files
#     )
#     return updated_comment


@router.get("/{comment_id}/files/{file_id}")
async def download_comment_file(
    *,
    session: AsyncSessionDep,
    _current_user: CurrentUserAsync,
    comment_id: UUID,
    file_id: UUID,
) -> Any:
    """
    Скачать файл комментария.
    """
    comment_file = await get_comment_file_async(
        session=session, comment_id=comment_id, file_id=file_id
    )
    if not comment_file:
        raise HTTPException(status_code=404, detail="File not found")

    return await get_file_response(file_path=comment_file.file)
