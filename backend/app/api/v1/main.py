from fastapi import APIRouter

from app.api.v1.routes import (
    appeal_statuses,
    appeals,
    comments,
    contracts,
    login,
    organizations,
    private,
    regions,
    reports,
    representatives,
    tasks,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(appeals.router)
api_router.include_router(appeal_statuses.router)
api_router.include_router(comments.router)
api_router.include_router(organizations.router)
api_router.include_router(representatives.router)
api_router.include_router(contracts.router)
api_router.include_router(tasks.router)
api_router.include_router(regions.router)
api_router.include_router(utils.router)
api_router.include_router(reports.router)
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
