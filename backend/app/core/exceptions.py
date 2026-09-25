from typing import Any, Optional
from fastapi import HTTPException, status


class CustomAPIException(HTTPException):
    def __init__(self, status_code: int, code: str, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "details": details}
        )


class EntityNotFoundException(CustomAPIException):
    def __init__(self, message: str = "Requested resource not found", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details
        )


class DuplicateEntityException(CustomAPIException):
    def __init__(self, message: str = "Resource already exists", details: Optional[Any] = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            code="DUPLICATE_RESOURCE",
            message=message,
            details=details
        )


class AuthenticationFailedException(CustomAPIException):
    def __init__(self, message: str = "Invalid authentication credentials", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="AUTHENTICATION_FAILED",
            message=message,
            details=details
        )


class PermissionDeniedException(CustomAPIException):
    def __init__(self, message: str = "Operation not permitted for your role", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="PERMISSION_DENIED",
            message=message,
            details=details
        )


class InsufficientContentException(CustomAPIException):
    def __init__(self, message: str = "Publication content is insufficient for analysis", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="INSUFFICIENT_CONTENT",
            message=message,
            details=details
        )


class ProviderServiceException(CustomAPIException):
    def __init__(self, message: str = "Upstream AI/Analysis provider failed", details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            code="PROVIDER_ERROR",
            message=message,
            details=details
        )
