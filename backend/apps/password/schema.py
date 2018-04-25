from marshmallow import Schema
from base.schema import BaseSchema
from base import schema_fields as fields


class QuestionSchema(BaseSchema):
    data_type = fields.Function(lambda obj: obj.data_type.value)

    class Meta:
        fields = ("id", "text", "password_text", "data_type", "related_id")


class PasswordSchema(BaseSchema):
    class Meta:
        fields = ("id", "name", "questions")


class AnswerItemSchema(Schema):
    """
    This schema is used to collect individual answers to the questions that will generate a password.
    Since we never store the answers, this schema does not have a Model behind it.
    """

    question_id = fields.Integer(required=True)
    answer = fields.String(required=True)


class AnswerSchema(Schema):
    """
    This schema is used to collect the set of answers to generate a password.
    Since we never store the answers, this schema does not have a Model behind it.
    """

    password_id = fields.String(required=True)
    answers = fields.Nested(AnswerItemSchema, many=True)


class GeneratedPasswordSchema(Schema):
    """
    This schema is used to return the generate password.
    This schema does not have a Model associated since the data is never stored.
    """

    password = fields.String(dump_only=True)
