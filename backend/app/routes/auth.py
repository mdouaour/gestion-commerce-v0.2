from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.core.errors import ErrorCode
from app.routes.deps import get_db, raise_http_exception
from app.schemas.user import Token
from app.services.user_service import UserService

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await UserService.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INVALID_CREDENTIALS)
    elif not user.is_active:
        raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INACTIVE_USER)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.username, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
