import io
from datetime import date, datetime
from uuid import UUID

import pandas as pd
from sqlmodel import Session, select

from app.models.appeal import Appeal
from app.models.representative import Representative


def get_date_display(dt: datetime | None) -> str:
    if not dt or not isinstance(dt, datetime):
        return "-"
    return dt.strftime("%Y-%m-%d %H:%M")


def get_list_data(appeals: list[Appeal]) -> list:
    """Функция для получения списка данных по заявкам для формирования dataframe"""
    list_data = []

    for appeal in appeals:
        # Получаем список ответственных пользователей
        responsible_users = {
            specialist.user.get_full_name() for specialist in appeal.specialists
        }
        responsible = ", ".join(responsible_users)

        # Получаем полное имя представителя
        person_fullname = f"{appeal.user.last_name} {appeal.user.first_name}"
        if appeal.user.middle_name:
            person_fullname += f" {appeal.user.middle_name}"

        row_data = [
            str(appeal.id),  # Используем ID вместо номера
            appeal.user.representative.organization.name,
            person_fullname,
            appeal.priority.name if appeal.priority else "-",
            appeal.project.name if appeal.project else "-",
            appeal.description,
            get_date_display(appeal.created_at),
            responsible,
            get_date_display(appeal.actual_date),
            appeal.status.name if appeal.status else "-",
            appeal.solution or "-",
        ]
        list_data.append(row_data)

    return list_data


def generate_organization_report(
    *,
    session: Session,
    organization_id: UUID,
    date_from: date,
    date_to: date,
) -> str:
    """Генерация отчета по обращениям организации за период"""
    # Создаем временный файл
    file = io.BytesIO()

    # Получаем пользователей организации через представителей
    representatives = session.exec(
        select(Representative).where(Representative.organization_id == organization_id)
    ).all()
    user_ids = [rep.user_id for rep in representatives]

    # Получаем обращения
    appeals = session.exec(
        select(Appeal)
        .where(
            Appeal.user_id.in_(user_ids),
            Appeal.created_at >= datetime.combine(date_from, datetime.min.time()),
            Appeal.created_at <= datetime.combine(date_to, datetime.max.time()),
        )
        .order_by(Appeal.created_at)
    ).all()

    # Формируем DataFrame
    report_data = pd.DataFrame(
        get_list_data(appeals),
        columns=[
            "ID номер",
            "Заказчик",
            "Данные заказчика",
            "Уровни приоритета",
            "Продукт",
            "Описание обращения",
            "Дата создания",
            "Ответственные",
            "Дата решения",
            "Статус выполнения",
            "Решение",
        ],
    )

    # Записываем в Excel
    with pd.ExcelWriter(file) as writer:
        report_data.to_excel(writer, sheet_name="Report", index=False)
        # Автоподбор ширины колонок
        worksheet = writer.sheets["Report"]
        for idx, col in enumerate(report_data.columns):
            max_length = max(report_data[col].astype(str).apply(len).max(), len(col))
            worksheet.set_column(idx, idx, max_length + 2)

    file.seek(0)
    return file
