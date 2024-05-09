from app.store.telegram_api.dataclasses import (CallbackQuery, MessageEntity,
                                                Update, UpdateMessage,
                                                UpdateObject, User)


def parse_message(result: dict) -> Update:
    update = Update(
        update_id=result["update_id"],
        object=UpdateObject(
            message=UpdateMessage(
                message_id=result["message"]["message_id"],
                from_=User(
                    telegram_id=result["message"]["from"]["id"],
                    first_name=result["message"]["from"]["first_name"],
                    last_name=result["message"]["from"]["last_name"],
                    username=result["message"]["from"]["username"],
                ),
                chat_id=result["message"]["chat"]["id"],
                text=result["message"].get("text"),
                date=result["message"]["date"],
                entities=[MessageEntity(
                    type=result["message"].get("entities")[-1]["type"] if
                    result["message"].get("entities") else None,
                )],
            ),
        ),
    )
    return update


def parse_callback_query(result: dict) -> Update:
    update = Update(
            update_id=result["update_id"],
            object=UpdateObject(
                callback_query=CallbackQuery(
                    callback_id=result["callback_query"]["id"],
                    from_=User(
                        telegram_id=result["callback_query"]["from"]["id"],
                        first_name=result["callback_query"]["from"]["first_name"],
                        last_name=result["callback_query"]["from"]["last_name"],
                        username=result["callback_query"]["from"]["username"],
                    ),
                    chat_id=result["callback_query"]["message"]["chat"]["id"],
                    date=result["callback_query"]["message"]["date"],
                    data=result["callback_query"]["data"],
                ),
            )
        )
    return update
