from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile
from sqlmodel import Session, select

from app.core.files import save_upload_file
from app.models.appeal import Appeal, AppealBase
from app.models.appeal_file import AppealFile
from app.models.representative import Representative
from app.models.user import User


def create_appeal(
    *,
    session: Session,
    user: User,
    appeal: AppealBase,
    files: list[UploadFile] | None = None,
) -> Appeal:
    """Создание обращения"""
    db_appeal = Appeal.model_validate(
        appeal,
        update={
            "user_id": user.id,
            "region_id": user.representative.organization.region_id,
            "dt": datetime.now(timezone.utc),
        },
    )

    session.add(db_appeal)
    session.commit()
    session.refresh(db_appeal)

    # Сохраняем файлы, если они есть
    if files:
        for file in files:
            # Сохраняем файл и получаем путь
            file_path = save_upload_file(
                file=file,
                folder="appeal",
                entity_id=db_appeal.id,
            )

            # Создаем запись в БД
            appeal_file = AppealFile(
                appeal_id=db_appeal.id,
                file=file_path,
            )
            session.add(appeal_file)

        session.commit()

    return db_appeal


def get_appeal(*, session: Session, appeal_id: UUID) -> Appeal | None:
    """Получение обращения по ID"""
    return session.get(Appeal, appeal_id)


def get_appeals(
    *, session: Session, user: User, skip: int = 0, limit: int = 100
) -> list[Appeal]:
    """Получение списка обращений с учетом прав пользователя"""
    query = select(Appeal)

    if not user.is_superuser:
        if hasattr(user, "representative"):
            # Для представителя организации
            query = query.where(Appeal.user_id == user.id)
        elif hasattr(user, "specialist"):
            # Для специалиста
            controlled_orgs = user.specialist.controlled_organizations
            query = query.where(
                Appeal.user_id.in_(
                    select(User.id)
                    .join(User.representative)
                    .where(
                        Representative.organization_id.in_(
                            [org.id for org in controlled_orgs]
                        )
                    )
                )
            )

    appeals = session.exec(query.offset(skip).limit(limit)).all()
    return appeals


def update_appeal(
    *,
    session: Session,
    db_appeal: Appeal,
    status_id: UUID | None = None,
    responsible_user_id: UUID | None = None,
    solving: str | None = None,
    **kwargs,
) -> Appeal:
    """Обновление обращения"""
    update_data = {k: v for k, v in kwargs.items() if v is not None}

    if status_id is not None:
        update_data["status_id"] = status_id
        if status_id == "done":  # Замените на реальный ID статуса "done"
            update_data["actual_date"] = datetime.utcnow()

    if responsible_user_id is not None:
        update_data["responsible_user_id"] = responsible_user_id

    if solving is not None:
        update_data["solving"] = solving

    db_appeal.sqlmodel_update(update_data)
    session.add(db_appeal)
    session.commit()
    session.refresh(db_appeal)
    return db_appeal


def delete_appeal(*, session: Session, appeal_id: UUID) -> None:
    """Удаление обращения"""
    appeal = session.get(Appeal, appeal_id)
    if appeal:
        session.delete(appeal)
        session.commit()


# def get_appeals_paginated(
#     *, session: Session, user: User, pagination: PaginationParams
# ) -> PaginatedResponse[Appeal]:
#     """Получение списка обращений с пагинацией"""
#     query = select(Appeal)

#     if not user.is_superuser:
#         if hasattr(user, "representative"):
#             query = query.where(Appeal.user_id == user.id)
#         elif hasattr(user, "specialist"):
#             controlled_orgs = user.specialist.controlled_organizations
#             query = query.where(
#                 Appeal.user_id.in_(
#                     select(User.id)
#                     .join(User.representative)
#                     .where(
#                         Representative.organization_id.in_(
#                             [org.id for org in controlled_orgs]
#                         )
#                     )
#                 )
#             )

#     return paginate_query(session, query, pagination)
