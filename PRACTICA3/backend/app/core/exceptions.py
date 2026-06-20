class ApplicationError(Exception):
    """Base exception for expected application errors."""


class ResourceNotFoundError(ApplicationError):
    pass


class ResourceConflictError(ApplicationError):
    pass


class AuthenticationError(ApplicationError):
    pass


class AuthorizationError(ApplicationError):
    pass


class BusinessRuleError(ApplicationError):
    pass


class InvalidFileError(ApplicationError):
    pass
