from sqlmodel import SQLModel

from app.models.appeal import Appeal, AppealBase
from app.models.appeal_file import AppealFile, AppealFileBase
from app.models.appeal_status import AppealStatus, AppealStatusBase
from app.models.appeal_stop_interval import AppealStopInterval, AppealStopIntervalBase
from app.models.auth import NewPassword, Token, TokenPayload
from app.models.comment import Comment, CommentBase
from app.models.comment_file import CommentFile, CommentFileBase
from app.models.common import (
    ErrorResponse,
    Message,
    UniversalPaginatedResponse,
    UniversalPaginationParams,
)
from app.models.contract import (
    Contract,
    ContractBase,
    ContractCreate,
    ContractRead,
    ContractUpdate,
)
from app.models.department import (
    Department,
    DepartmentBase,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
)
from app.models.organization import (
    Organization,
    OrganizationBase,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from app.models.priority import (
    BasePriorityBase,
    ContractStandardPriority,
    IndividualPriority,
    StandardPriority,
)
from app.models.project import OrganizationProject, Project, ProjectBase
from app.models.region import Region, RegionBase, RegionCreate, RegionRead, RegionUpdate
from app.models.representative import Representative, RepresentativeBase
from app.models.specialist import Specialist, SpecialistBase, SpecialistOrganization
from app.models.task import Task, TaskBase
from app.models.user import (
    UpdatePassword,
    User,
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

__all__ = [
    "SQLModel",
    # Auth
    "Token",
    "TokenPayload",
    "NewPassword",
    # Common
    "Message",
    "ErrorResponse",
    "UniversalPaginationParams",
    "UniversalPaginatedResponse",
    # Appeal
    "Appeal",
    "AppealBase",
    # Contract
    "Contract",
    "ContractBase",
    "ContractCreate",
    "ContractRead",
    "ContractUpdate",
    # Department
    "Department",
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentRead",
    "DepartmentUpdate",
    # Organization
    "Organization",
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationRead",
    "OrganizationUpdate",
    # Priority
    "BasePriorityBase",
    "StandardPriority",
    "IndividualPriority",
    "ContractStandardPriority",
    # Project
    "Project",
    "ProjectBase",
    "OrganizationProject",
    # Representative
    "Representative",
    "RepresentativeBase",
    # Specialist
    "Specialist",
    "SpecialistBase",
    "SpecialistOrganization",
    # Task
    "Task",
    "TaskBase",
    # User
    "User",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserPublic",
    "UsersPublic",
    "UserRegister",
    "UserUpdateMe",
    "UpdatePassword",
    # Region
    "Region",
    "RegionBase",
    "RegionCreate",
    "RegionRead",
    "RegionUpdate",
    # AppealFile
    "AppealFile",
    "AppealFileBase",
    # Comment
    "Comment",
    "CommentBase",
    # CommentFile
    "CommentFile",
    "CommentFileBase",
    # AppealStopInterval
    "AppealStopInterval",
    "AppealStopIntervalBase",
    # AppealStatus
    "AppealStatus",
    "AppealStatusBase",
]
