from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import BaseModel
from app.user.models import UserModel

__all__ = (
    "Exchange",
    "GameModel",
    "GameUser",
    "Phrase",
    "Session",
    "SessionStock",
    "Stock",
    "UserStock",
)


class GameModel(BaseModel):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    users: Mapped[list["GameUser"]] = relationship(
        "GameUser", back_populates="game", lazy="joined"
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="game"
    )
    stocks: Mapped[list["UserStock"]] = relationship(
        "UserStock",
        back_populates="game",
    )


class GameUser(BaseModel):
    __tablename__ = "game_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="RESTRICT"), nullable=False
    )
    cash_balance: Mapped[float] = mapped_column(default=0.0)

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="games"
    )
    game: Mapped["GameModel"] = relationship(
        "GameModel", back_populates="users"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "game_id", name="user_game_unique_constraint"
        ),
    )


class Session(BaseModel):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int] = mapped_column(default=1)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), nullable=False)
    is_finished: Mapped[bool] = mapped_column(default=False)

    game: Mapped["GameModel"] = relationship(
        "GameModel", back_populates="sessions"
    )
    stocks: Mapped[list["SessionStock"]] = relationship(
        "SessionStock",
        back_populates="session",
    )
    exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange",
        back_populates="session",
    )


class Stock(BaseModel):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(default=None)

    sessions: Mapped[list["SessionStock"]] = relationship(
        "SessionStock",
        back_populates="stock",
    )
    users: Mapped[list["UserStock"]] = relationship(
        "UserStock", back_populates="stock"
    )

    exchanges: Mapped[list["Exchange"]] = relationship(
        "Exchange", back_populates="stock"
    )

    __table_args__ = (
        UniqueConstraint("title", name="stock_title_unique_constraint"),
    )


class SessionStock(BaseModel):
    __tablename__ = "session_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id"), nullable=False
    )
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id"), nullable=False
    )
    price: Mapped[float] = mapped_column(default=0.0)

    session: Mapped["Session"] = relationship(
        "Session", back_populates="stocks"
    )
    stock: Mapped["Stock"] = relationship(
        "Stock", back_populates="sessions", lazy="joined"
    )


class UserStock(BaseModel):
    __tablename__ = "user_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id", ondelete="RESTRICT"), nullable=False
    )
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), nullable=False)
    total_quantity: Mapped[int] = mapped_column(default=0)

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="stocks"
    )
    stock: Mapped["Stock"] = relationship(
        "Stock", back_populates="users", lazy="joined"
    )

    game: Mapped["GameModel"] = relationship(
        "GameModel", back_populates="stocks"
    )


class Phrase(BaseModel):
    __tablename__ = "phrase"

    key: Mapped[str] = mapped_column(primary_key=True)
    phrase: Mapped[str] = mapped_column(default=None)


class Exchange(BaseModel):
    __tablename__ = "exchange"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id", ondelete="RESTRICT"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )
    chat_id: Mapped[str] = mapped_column(nullable=False)
    action: Mapped[str] = mapped_column(nullable=False)
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(default=0)
    execution_time: Mapped[datetime] = mapped_column(default=datetime.now())

    session: Mapped["Session"] = relationship(
        "Session", back_populates="exchanges"
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="exchanges"
    )

    stock: Mapped["Stock"] = relationship("Stock", back_populates="exchanges")
