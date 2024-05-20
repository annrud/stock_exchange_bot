from app.telegram_bot.dataclasses import (
    CallbackQuery,
    From,
    MessageEntity,
    ReplyMessage,
    Update,
    UpdateMessage,
    UpdateObject,
)


def parse_message(result: dict) -> Update:
    msg = result["message"]
    msg_from = msg["from"]
    entities = msg.get("entities")
    update = Update(
        update_id=result["update_id"],
        object=UpdateObject(
            message=UpdateMessage(
                message_id=msg["message_id"],
                from_=From(
                    telegram_id=msg_from["id"],
                    first_name=msg_from["first_name"],
                    last_name=msg_from.get("last_name"),
                    username=msg_from.get("username"),
                ),
                chat_id=str(msg["chat"]["id"]),
                text=msg.get("text"),
                date=msg["date"],
                entities=[
                    MessageEntity(
                        type=entities[-1]["type"] if entities else None,
                    )
                ],
                reply_to_message=None,
            )
        ),
    )
    reply_to_message = msg.get("reply_to_message")
    if reply_to_message:
        update.object.message.reply_to_message = ReplyMessage(
            message_id=reply_to_message["message_id"],
            from_=From(
                telegram_id=reply_to_message["from"]["id"],
                first_name=reply_to_message["from"]["first_name"],
                last_name=reply_to_message["from"].get("last_name"),
                username=reply_to_message["from"].get("username"),
            ),
            chat_id=reply_to_message["chat"]["id"],
            text=reply_to_message["text"],
        )
    return update


def parse_callback_query(result: dict) -> Update:
    callback = result["callback_query"]
    callback_from = callback["from"]
    callback_msg = callback["message"]
    return Update(
        update_id=result["update_id"],
        object=UpdateObject(
            callback_query=CallbackQuery(
                callback_id=callback["id"],
                from_=From(
                    telegram_id=callback_from["id"],
                    first_name=callback_from["first_name"],
                    last_name=callback_from.get("last_name"),
                    username=callback_from.get("username"),
                ),
                chat_id=str(callback_msg["chat"]["id"]),
                date=callback_msg["date"],
                data=callback["data"],
            ),
        ),
    )
