from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import BaseModel
from app.user.models import User


class Game(BaseModel):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    users: Mapped[List["GameUser"]] = relationship(
        "GameUser",
        back_populates="game",
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="game"
    )


class GameUser(BaseModel):
    __tablename__ = "game_user"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="games")
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="RESTRICT"), nullable=False
    )
    game: Mapped["Game"] = relationship("Game", back_populates="users")
    cash_balance: Mapped[float] = mapped_column(default=0.0)


class Session(BaseModel):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(default=None)
    game_id: Mapped[int] = mapped_column(ForeignKey("game.id"), nullable=False)
    game: Mapped["Game"] = relationship("Game", back_populates="sessions")
    is_finished: Mapped[bool] = mapped_column(default=False)
    stocks: Mapped[List["SessionStock"]] = relationship(
        "SessionStock",
        back_populates="session",
    )


class Stock(BaseModel):
    __tablename__ = "stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(default=None)
    sessions: Mapped[List["SessionStock"]] = relationship(
        "SessionStock",
        back_populates="stock",
    )
    users: Mapped[List["UserStock"]] = relationship(
        "UserStock", back_populates="stock"
    )


class SessionStock(BaseModel):
    __tablename__ = "session_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("session.id"), nullable=False
    )
    session: Mapped["Session"] = relationship(
        "Session", back_populates="stocks"
    )
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id"), nullable=False
    )
    stock: Mapped["Stock"] = relationship(
        "Stock", back_populates="sessions"
    )
    price: Mapped[float] = mapped_column(default=0.0)


class UserStock(BaseModel):
    __tablename__ = "user_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="stocks")
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("stock.id", ondelete="RESTRICT"), nullable=False
    )
    stock: Mapped["Stock"] = relationship("Stock", back_populates="users")
    buy_quantity: Mapped[int] = mapped_column(default=0)
    sell_quantity: Mapped[int] = mapped_column(default=0)


class Phrase(BaseModel):
    __tablename__ = "phrase"

    key: Mapped[str] = mapped_column(primary_key=True)
    phrase: Mapped[str] = mapped_column(default=None)
