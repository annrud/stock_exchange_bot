import typing
import importlib
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import BaseModel


class User(BaseModel):
    __tablename__ = "user"
    importlib.import_module("app.game.models")

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column(default=None)
    username: Mapped[str] = mapped_column(unique=True)

    games: Mapped[typing.List["GameUser"]] = relationship(
        "GameUser", back_populates="user",
    )

    stocks: Mapped[typing.List["UserStock"]] = relationship(
        "UserStock", back_populates="user"
    )
