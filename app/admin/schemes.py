from marshmallow import Schema, fields

from app.web.schemes import OkResponseSchema

__all__ = (
    "AdminResponseSchema",
    "AdminSchema",
)


class AdminSchema(Schema):
    id = fields.Int(required=False)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class AdminResponseSchema(OkResponseSchema):
    data = fields.Nested(AdminSchema)
