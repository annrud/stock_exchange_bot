from dataclasses import asdict, dataclass

__all__ = (
    "CallbackQuery",
    "From",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "Message",
    "MessageEntity",
    "Update",
    "UpdateMessage",
    "UpdateObject",
)


@dataclass
class InlineKeyboardButton:
    text: str
    url: str = ""
    callback_data: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: list[list[InlineKeyboardButton]]


@dataclass
class Message:
    chat_id: str
    text: str = ""
    reply_markup: dict[str, InlineKeyboardMarkup] | None = None


@dataclass
class From:
    telegram_id: int
    first_name: str
    last_name: str | None = None
    username: str | None = None


@dataclass
class MessageEntity:
    type: str | None = None


@dataclass
class UpdateMessage:
    message_id: int
    from_: From
    chat_id: str
    date: int
    entities: list[MessageEntity]
    text: str


@dataclass
class CallbackQuery:
    callback_id: str
    from_: From
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
