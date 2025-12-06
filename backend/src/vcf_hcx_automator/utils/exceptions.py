from typing import Optional, Dict, Any

class AutomatorException(Exception):
    """Base exception for VCF HCX Automator"""
    def __init__(
        self, 
        message: str, 
        code: str = "INTERNAL_ERROR", 
        details: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.remediation = remediation
        super().__init__(self.message)

class ConfigurationError(AutomatorException):
    """Configuration related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message, 
            code="CONFIG_ERROR", 
            details=details,
            remediation="Check your configuration settings and environment variables."
        )

class APIError(AutomatorException):
    """External API related errors"""
    def __init__(
        self, 
        message: str, 
        status_code: int, 
        provider: str,
        details: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ):
        details = details or {}
        details.update({"status_code": status_code, "provider": provider})
        super().__init__(
            message=message,
            code=f"{provider.upper()}_API_ERROR",
            details=details,
            remediation=remediation or "Check the external system status and connectivity."
        )

class AuthenticationError(APIError):
    """Authentication failures"""
    def __init__(self, message: str, provider: str):
        super().__init__(
            message=message,
            status_code=401,
            provider=provider,
            remediation="Verify your credentials and permissions."
        )

class ResourceNotFoundError(APIError):
    """Resource not found errors"""
    def __init__(self, message: str, provider: str, resource_type: str, resource_id: str):
        super().__init__(
            message=message,
            status_code=404,
            provider=provider,
            details={"resource_type": resource_type, "resource_id": resource_id},
            remediation=f"Verify that the {resource_type} with ID {resource_id} exists."
        )
