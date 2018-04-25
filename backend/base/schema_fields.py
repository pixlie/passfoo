from marshmallow import fields
from marshmallow.exceptions import ValidationError

from base.error_handler import Error


class defaults:
    __classname__ = 'defaults'

    default_error_messages = {
        'required': Error.MISSING_REQUIRED_FIELD.name,
        'type': Error.INVALID_INPUT_TYPE.name,  # used by Unmarshaller
        'null': Error.NULL_FIELD_NOT_ALLOWED.name,
        'validator_failed': Error.INVALID_VALUE.name,
        'invalid': Error.INVALID_VALUE.name,
        'invalid_utf8': Error.INVALID_VALUE.name,
        'format': '"{input}" cannot be formatted as a %s.' % __classname__
    }


class String(defaults, fields.String):
    __classname__ = 'string'


class Number(defaults, fields.Number):
    __classname__ = 'number'


class Integer(defaults, fields.Integer):
    __classname__ = 'integer'


class Decimal(defaults, fields.Decimal):
    __classname__ = 'decimal'

    def __init__(self, *args, **kwargs):
        super(fields.Decimal, self).__init__(*args, **kwargs)
        self.default_error_messages['special'] = 'Special numeric values are not permitted.'


class Boolean(defaults, fields.Boolean):
    __classname__ = 'boolean'

    def __init__(self, *args, **kwargs):
        super(fields.Boolean, self).__init__(*args, **kwargs)
        self.default_error_messages['invalid'] = 'Not a valid boolean.'


class FormattedString(defaults, fields.FormattedString):
    __classname__ = 'string'

    def __init__(self, *args, **kwargs):
        super(fields.FormattedString, self).__init__(*args, **kwargs)
        self.default_error_messages['format'] = 'Cannot format string with given data.'


class DateTime(defaults, fields.DateTime):
    __classname__ = 'datetime'


class Date(defaults, fields.Date):
    __classname__ = 'date'


class Time(defaults, fields.TimeDelta):
    __classname__ = 'time'

    def __init__(self, *args, **kwargs):
        super(fields.TimeDelta, self).__init__(*args, **kwargs)
        self.default_error_messages['format'] = '{input!r} cannot be formatted as timedelta'


class Float(defaults, fields.Float):
    __classname__ = 'float'


class Email(defaults, fields.Email):
    __classname__ = 'email'


class Nested(defaults, fields.Nested):
    __classname__ = 'nested'


class Enum(defaults, fields.Field):
    __classname__ = 'enum'

    def _serialize(self, value, attr, obj):
        try:
            return value.name
        except Exception as e:
            raise ValidationError(Error.INVALID_VALUE.name)

    def _deserialize(self, value, attr, data):
        try:
            enum_type = self.metadata["enum_type"]
            return enum_type[value]
        except Exception as e:
            raise ValidationError(Error.INVALID_VALUE.name)


class Method(defaults, fields.Method):
    __classname__ = 'method'


class Function(defaults, fields.Function):
    __classname__ = 'function'
