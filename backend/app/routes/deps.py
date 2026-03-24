from typing import Generator, Optional, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.config import settings
from app.core.database import SessionLocal, get_db
from app.core.errors import ErrorCode
from app.models.user import User, UserRole
from app.schemas.user import TokenData
from app.services.user_service import UserService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

# Centralized HTTP Exception with error code
def raise_http_exception(status_code: int, code: ErrorCode, detail: Optional[str] = None):
    # The detail is a fallback for developers, not for end-users.
    # The frontend should use the 'code' for translation.
    raise HTTPException(status_code=status_code, detail={"code": code.value, "detail": detail or code.name})

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenData(username=payload.get("sub"))
    except (JWTError, ValidationError):
        raise_http_exception(status.HTTP_403_FORBIDDEN, ErrorCode.AUTH_FORBIDDEN, "Could not validate credentials")
    
    user = await UserService.get_by_username(db, username=token_data.username)
    if not user:
        raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.AUTH_USER_NOT_FOUND)
    if not user.is_active:
        raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INACTIVE_USER)
    return user

def check_admin(user: User = Depends(get_current_user)):
    if user.role != UserRole.ADMIN:
        raise_http_exception(status.HTTP_403_FORBIDDEN, ErrorCode.AUTH_FORBIDDEN, "The user doesn't have enough privileges")
    return user
