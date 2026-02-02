"""
Shared Exception Definitions
Used across services for consistent error handling
"""


class ServiceError(Exception):
    """Base exception for service errors"""
    pass


class ValidationError(ServiceError):
    """Data validation error"""
    pass


class AuthenticationError(ServiceError):
    """Authentication failed"""
    pass


class AuthorizationError(ServiceError):
    """Authorization failed (insufficient permissions)"""
    pass


class NotFoundError(ServiceError):
    """Resource not found"""
    pass


class ConflictError(ServiceError):
    """Resource conflict (e.g., duplicate entry)"""
    pass


class ExternalServiceError(ServiceError):
    """Error calling external service"""
    pass
