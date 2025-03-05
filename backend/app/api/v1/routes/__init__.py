from .appeal_statuses import router as appeal_statuses_router
from .appeal_stop_intervals import router as appeal_stop_intervals_router
from .appeals import router as appeals_router
from .comments import router as comments_router
from .contracts import router as contracts_router
from .login import router as login_router
from .organizations import router as organizations_router
from .private import router as private_router
from .regions import router as regions_router
from .reports import router as reports_router
from .representatives import router as representatives_router
from .tasks import router as tasks_router
from .users import router as users_router
from .utils import router as utils_router

__all__ = [
    "appeal_statuses_router",
    "appeal_stop_intervals_router",
    "appeals_router",
    "comments_router",
    "contracts_router",
    "login_router",
    "organizations_router",
    "private_router",
    "regions_router",
    "representatives_router",
    "reports_router",
    "tasks_router",
    "users_router",
    "utils_router",
]
