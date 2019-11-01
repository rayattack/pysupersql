__all__ = ("InvalidFieldError", "ValidationError")


class _Exception(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        msg = kwargs.get("msg", "Supersql exception")
        origin = kwargs.get("origin")

        self.msg = f"{msg} raised at: {origin}"

class ArgumentError(_Exception):
    pass


class DuplicateError(Exception):
    pass


class InvalidDocumentError(Exception):
    pass


class InvalidFieldError(Exception):
    pass


class NotFoundError(Exception):
    pass


class OfflineDocumentError(Exception):
    pass


class PKError(Exception):
    pass


class UnknownFieldError(Exception):
    pass


class ValidationError(Exception):
    pass
