from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(required=False)
    telegram_id = fields.Int(required=True)
    first_name = fields.Str(required=False)
    username = fields.Str(required=False)


class UserListSchema(Schema):
    users = fields.Nested(UserSchema, many=True)
