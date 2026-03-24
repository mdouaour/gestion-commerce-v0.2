from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.errors import ErrorCode
from app.routes.deps import raise_http_exception
from fastapi import HTTPException, status
from typing import List, Optional

class UserService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: UserCreate) -> User:
        user = await UserService.get_by_username(db, username=obj_in.username)
        if user:
            raise_http_exception(
                status.HTTP_400_BAD_REQUEST, 
                ErrorCode.USER_ALREADY_EXISTS, 
                "The user with this username already exists in the system."
            )
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=obj_in.is_active
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate(
        db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        user = await UserService.get_by_username(db, username)
        if not user:
            # This error message is intentionally generic for security reasons
            raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INVALID_CREDENTIALS)
        if not user.is_active:
            raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INACTIVE_USER)
        if not verify_password(password, user.hashed_password):
            raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.AUTH_INVALID_CREDENTIALS)
        return user

    @staticmethod
    async def get_all(db: AsyncSession) -> List[User]:
        result = await db.execute(select(User))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
