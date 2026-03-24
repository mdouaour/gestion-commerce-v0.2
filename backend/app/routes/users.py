from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.routes.deps import get_db, get_current_user, check_admin

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=User, dependencies=[Depends(check_admin)])
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await UserService.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return await UserService.create(db, obj_in=user_in)

@router.get("/", response_model=List[User], dependencies=[Depends(check_admin)])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    return await UserService.get_all(db)
