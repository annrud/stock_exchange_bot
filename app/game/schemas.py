from marshmallow import Schema, fields


class ExchangeSchema(Schema):
    id = fields.Int(required=False)
    session_id = fields.Int()
    user_id = fields.Int()
    chat_id = fields.Str()
    action = fields.Str()
    stock_id = fields.Int()
    quantity = fields.Int()
    execution_time = fields.DateTime()


class ExchangeListSchema(Schema):
    users = fields.Nested(ExchangeSchema, many=True)


class UserIdSchema(Schema):
    user_id = fields.Int()
