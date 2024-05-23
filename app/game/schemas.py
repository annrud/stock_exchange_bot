from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    telegram_id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    username = fields.Str()


class StockSchema(Schema):
    id = fields.Int()
    title = fields.Str()


class ExchangeSchema(Schema):
    id = fields.Int(required=False)
    session_id = fields.Int()
    user = fields.Nested(UserSchema)
    chat_id = fields.Str()
    action = fields.Str()
    stock = fields.Nested(StockSchema)
    quantity = fields.Int()
    execution_time = fields.DateTime()


class ExchangeListSchema(Schema):
    users = fields.Nested(ExchangeSchema, many=True)


class UserIdSchema(Schema):
    user_id = fields.Int()
