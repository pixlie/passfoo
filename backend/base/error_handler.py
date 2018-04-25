from enum import Enum
from base.db import db


class Error(Enum):
    INVALID_EMAIL_PASSWORD = 1
    PASSWORD_MISMATCH = 2
    EMAIL_ID_NOT_FOUND = 3
    EMAIL_ALREADY_VERIFIED = 4
    EMAIL_VERIFICATION_FAILED = 5
    INVALID_PHONE_NUMBER = 6
    PHONE_VERIFICATION_FAILED = 7
    INVALID_TOKEN = 8
    NOT_AUTHORISED = 9
    DATABASE_WRITE_FAIL = 10
    METHOD_NOT_ALLOWED = 11
    DATA_NOT_FOUND = 12
    MISSING_REQUIRED_FIELD = 13
    INVALID_INPUT_TYPE = 14
    NULL_FIELD_NOT_ALLOWED = 15
    INVALID_VALUE = 16

    @classmethod
    def handle_schema_errors(cls, error_dict, errors):
        for key, value in error_dict.items():
            if type(value) is list:
                errors.append({
                    "code": Error[value[0]].value,
                    "message": value[0],
                    "field": key,
                    "context": None
                })
            elif type(value) is dict:
                for field, message in value.items():
                    errors.append({
                        "code": Error[message[0]].value,
                        "message": message[0],
                        "field": "%s.%s" % (key, field),
                        "context": None
                    })
        return errors

    @classmethod
    def handle_invalid_method_error(cls, method_name, errors):
        errors.append({
            "code": Error.METHOD_NOT_ALLOWED.value,
            "message": Error.METHOD_NOT_ALLOWED.name,
            "field": method_name,
            "context": None
        })

        return errors

    @classmethod
    def handle_data_not_found_errors(cls, errors):
        errors.append({
            "code": Error.DATA_NOT_FOUND.value,
            "message": Error.DATA_NOT_FOUND.name,
            "field": None,
            "context": None
        })

        return errors

    @classmethod
    def handle_database_write_fail(cls, errors, data):
        field, context = "", ""
        if data:
            if hasattr(data, "orig") and hasattr(data.orig, "diag"):
                error_obj = data.orig.diag
                if hasattr(error_obj, "column_name") and error_obj.column_name:
                    field = error_obj.column_name
                else:
                    field = error_obj.constraint_name

                context = error_obj.message_detail

        errors.append({
            "code": Error.DATABASE_WRITE_FAIL.value,
            "message": Error.DATABASE_WRITE_FAIL.name,
            "field": field,
            "context": context
        })

        return errors

    @classmethod
    def handle_custom_errors(cls, data, errors):
        errors.append({
            "code": data["error_code"].value,
            "message": data["error_code"].name,
            "field": data["field"],
            "context": data["context"]
        })

        return errors

    @classmethod
    def generate_error(cls, type, data=None, prev_errors=None):
        if prev_errors is None:
            prev_errors = []
        if type == ErrorType.SCHEMA_ERROR:
            return cls.handle_schema_errors(data, prev_errors)

        elif type == ErrorType.INVALID_METHOD:
            return cls.handle_invalid_method_error(data, prev_errors)

        elif type == ErrorType.DATA_NOT_FOUND:
            return cls.handle_data_not_found_errors(prev_errors)

        elif type == ErrorType.DATABASE_WRITE_FAIL:
            db.session.rollback()
            return cls.handle_database_write_fail(data=data, errors=prev_errors)

        elif type == ErrorType.CUSTOM_ERRORS:
            return cls.handle_custom_errors(data, prev_errors)


class ErrorType(Enum):
    SCHEMA_ERROR = 1
    INVALID_METHOD = 2
    DATA_NOT_FOUND = 3
    DATABASE_WRITE_FAIL = 4
    CUSTOM_ERRORS = 5
