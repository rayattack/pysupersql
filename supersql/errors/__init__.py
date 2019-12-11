__all__ = ("InvalidFieldError", "ValidationError")


class _Exception(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        msg = kwargs.get("msg", "Supersql exception")
        origin = kwargs.get("origin")

        self.msg = f"{msg} raised at: {origin}"


class Error(_Exception):
    pass


class InterfaceError(Exception):
    pass


class DatabaseError(Exception):
    pass


class DataError(Exception):
    pass


class OperationalError(_Exception):
    pass


class IntegrityError(Exception):
    pass


class InternalError(Exception):
    pass


class ProgrammingError(Exception):
    pass


class NotSupportedError(Exception):
    pass


# Library Errors

class ArgumentError(_Exception):
    pass


class DuplicateError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


class MissingArgumentError(Exception):
    pass


class MissingCommandError(_Exception):
    pass


class PKError(Exception):
    pass


class UnknownFieldError(Exception):
    pass


class ValidationError(Exception):
    pass
