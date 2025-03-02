from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.v1.deps import SessionDep, get_current_user
from app.models.user import User
from app.utils.reports import generate_organization_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/organization/{organization_id}")
def get_organization_report(
    *,
    session: SessionDep,
    organization_id: UUID,
    date_from: date,
    date_to: date,
    _: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Генерация отчета по обращениям организации за период.

    Args:
        organization_id: ID организации
        date_from: Начальная дата периода
        date_to: Конечная дата периода

    Returns:
        StreamingResponse: Excel-файл с отчетом
    """
    file = generate_organization_report(
        session=session,
        organization_id=organization_id,
        date_from=date_from,
        date_to=date_to,
    )

    filename = f"organization_report_{date_from}_{date_to}.xlsx"

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
