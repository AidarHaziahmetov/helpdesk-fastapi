from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.cruds.appeal_status import create_appeal_status
from app.cruds.user import create_user
from app.models.appeal_status import AppealStatus
from app.models.user import User, UserCreate

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
async_engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI).replace(
        "postgresql://", "postgresql+asyncpg://"
    )
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = create_user(session=session, user_create=user_in)
    default_appeal_status = session.exec(
        select(AppealStatus).where(AppealStatus.name == "New")
    ).first()
    if not default_appeal_status:
        create_appeal_status(
            session=session, appeal_status_in=AppealStatus(name="New", name_rus="Новое")
        )
