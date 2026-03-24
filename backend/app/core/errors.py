from enum import Enum
from fastapi import HTTPException, status

class ErrorCode(str, Enum):
    # Auth
    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_INACTIVE_USER = "AUTH_INACTIVE_USER"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"
    AUTH_USER_NOT_FOUND = "AUTH_USER_NOT_FOUND"

    # Resources
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    SKU_ALREADY_EXISTS = "SKU_ALREADY_EXISTS"
    SALE_NOT_FOUND = "SALE_NOT_FOUND"
    PARCEL_NOT_FOUND = "PARCEL_NOT_FOUND"
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"

    # Business Logic
    INSUFFICIENT_STOCK = "INSUFFICIENT_STOCK"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    OPTIMISTIC_LOCK_CONFLICT = "OPTIMISTIC_LOCK_CONFLICT"
    
    # Generic
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

# Centralized HTTP Exception with error code
def raise_http_exception(status_code: int, code: ErrorCode, detail: Optional[str] = None):
    # The detail is a fallback for developers, not for end-users.
    # The frontend should use the 'code' for translation.
    raise HTTPException(
        status_code=status_code, 
        detail={"code": code.value, "detail": detail or code.name}
    )
