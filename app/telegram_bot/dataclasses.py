from dataclasses import asdict, dataclass, field

__all__ = (
    "CallbackQuery",
    "ForceReply",
    "From",
    "InlineKeyboardButton",
    "InlineKeyboardMarkup",
    "Message",
    "MessageEntity",
    "ReplyMessage",
    "Update",
    "UpdateMessage",
    "UpdateObject",
)


@dataclass
class ForceReply:
    force_reply: bool
    input_field_placeholder: str
    selective: bool

    def to_dict(self):
        return asdict(self)


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
    reply_markup: dict[str, InlineKeyboardMarkup] = field(default_factory=dict)
    reply_to_message_id: int | None = None
    parse_mode: str | None = None


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
class ReplyMessage:
    message_id: int
    from_: From
    chat_id: str
    text: str


@dataclass
class UpdateMessage:
    message_id: int
    from_: From
    chat_id: str
    date: int
    entities: list[MessageEntity]
    text: str
    reply_to_message: ReplyMessage | None = None


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
