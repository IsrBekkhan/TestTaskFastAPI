from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import Base


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(unique=True)

    @classmethod
    async def create_statuses(cls, db_async_session: AsyncSession) -> None:
        statuses_data = [
            {"id": 1, "description": "в процессе"},
            {"id": 2, "description": "отправлен"},
            {"id": 3, "description": "доставлен"},
        ]
        statuses = [
            Status(id=status["id"], description=status["description"])
            for status in statuses_data
        ]

        try:
            async with db_async_session.begin():
                db_async_session.add_all(statuses)
        except IntegrityError:
            pass

