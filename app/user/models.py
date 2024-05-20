import importlib

from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import BaseModel

models = importlib.import_module("app.game.models")


class UserModel(BaseModel):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(default=None, nullable=True)
    last_name: Mapped[str] = mapped_column(default=None, nullable=True)
    username: Mapped[str] = mapped_column(default=None, nullable=True)

    games: Mapped[list["models.GameUser"]] = relationship(
        "GameUser",
        back_populates="user",
    )

    stocks: Mapped[list["models.UserStock"]] = relationship(
        "UserStock", back_populates="user"
    )

    exchanges: Mapped[list["models.Exchange"]] = relationship(
        "Exchange", back_populates="user"
    )

    __table_args__ = (
        UniqueConstraint("telegram_id", name="telegram_id_unique_constraint"),
    )
