"""
Custom exceptions for the application
"""
from fastapi import HTTPException


class TenantNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Tenant not found")


class InsufficientCreditsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=402, detail="Insufficient credits")


class UnauthorizedTenantAccessError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied to this tenant's resources")
