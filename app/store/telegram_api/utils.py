from app.store.telegram_api.dataclasses import (
    CallbackQuery,
    MessageEntity,
    Update,
    UpdateMessage,
    UpdateObject,
    User,
)


def parse_message(result: dict) -> Update:
    msg = result["message"]
    msg_from = msg["from"]
    entities = msg.get("entities")
    return Update(
        update_id=result["update_id"],
        object=UpdateObject(
            message=UpdateMessage(
                message_id=msg["message_id"],
                from_=User(
                    telegram_id=msg_from["id"],
                    first_name=msg_from["first_name"],
                    last_name=msg_from["last_name"],
                    username=msg_from["username"],
                ),
                chat_id=msg["chat"]["id"],
                text=msg.get("text"),
                date=msg["date"],
                entities=[
                    MessageEntity(
                        type=entities[-1]["type"] if entities else None,
                    )
                ],
            ),
        ),
    )


def parse_callback_query(result: dict) -> Update:
    callback = result["callback_query"]
    callback_from = callback["from"]
    callback_msg = callback["message"]
    return Update(
        update_id=result["update_id"],
        object=UpdateObject(
            callback_query=CallbackQuery(
                callback_id=callback["id"],
                from_=User(
                    telegram_id=callback_from["id"],
                    first_name=callback_from["first_name"],
                    last_name=callback_from["last_name"],
                    username=callback_from["username"],
                ),
                chat_id=callback_msg["chat"]["id"],
                date=callback_msg["date"],
                data=callback["data"],
            ),
        ),
    )
