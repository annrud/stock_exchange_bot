from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class InlineKeyboardButton:
    text: str
    url: str = ""
    callback_data: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class Message:
    chat_id: str
    text: str = ""
    reply_markup: Dict[str, InlineKeyboardMarkup] | None = None


@dataclass
class User:
    telegram_id: int
    first_name: str
    last_name: str
    username: str


@dataclass
class MessageEntity:
    type: str | None = None


@dataclass
class UpdateMessage:
    message_id: int
    from_: User
    chat_id: str
    date: int
    entities: list[MessageEntity]
    text: str


@dataclass
class CallbackQuery:
    callback_id: str
    from_: User
    chat_id: str | None = None
    data: str | None = None
    date: int | None = None


@dataclass
class UpdateObject:
    message: UpdateMessage | None = None
    callback_query: CallbackQuery | None = None


@dataclass
class Update:
    update_id: int
    object: UpdateObject
