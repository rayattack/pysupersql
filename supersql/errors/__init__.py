from typing import Optional, List

__all__ = (
    "InvalidFieldError",
    "ValidationError",
    "VendorDependencyError",
    "UnsupportedVendorError"
)


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


# Vendor Dependency Errors

class VendorDependencyError(ImportError):
    """Raised when a required vendor dependency is not installed."""

    def __init__(self, vendor: str, missing_deps: List[str], message: Optional[str] = None):
        self.vendor = vendor
        self.missing_deps = missing_deps

        if message is None:
            deps_str = ", ".join(missing_deps)
            message = (
                f"Missing required dependencies for {vendor}: {deps_str}\n"
                f"Install with: pip install supersql[{vendor}]\n"
                f"Or manually: pip install {' '.join(missing_deps)}"
            )

        super().__init__(message)


class UnsupportedVendorError(Exception):
    """Raised when an unsupported database vendor is specified."""

    def __init__(self, vendor: str, supported_vendors: Optional[List[str]] = None):
        self.vendor = vendor
        self.supported_vendors = supported_vendors or []

        if supported_vendors:
            supported_str = ", ".join(supported_vendors)
            message = (
                f"Unsupported database vendor: {vendor}\n"
                f"Supported vendors: {supported_str}"
            )
        else:
            message = f"Unsupported database vendor: {vendor}"

        super().__init__(message)
