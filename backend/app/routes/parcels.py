from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.parcel import Parcel, ParcelCreate, ParcelUpdate
from app.models.parcel import ParcelStatus
from app.services.parcel_service import ParcelService
from app.routes.deps import get_db, get_current_user

router = APIRouter()

@router.get("/", response_model=List[Parcel])
async def read_parcels(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve parcels.
    """
    return await ParcelService.get_all(db, skip=skip, limit=limit)

@router.post("/", response_model=Parcel)
async def create_parcel(
    *,
    db: AsyncSession = Depends(get_db),
    parcel_in: ParcelCreate,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Create new parcel.
    """
    return await ParcelService.create(db, obj_in=parcel_in, user_id=current_user.id)

@router.get("/{id}", response_model=Parcel)
async def read_parcel(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get parcel by ID.
    """
    parcel = await ParcelService.get(db, id=id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel

@router.put("/{id}/status", response_model=Parcel)
async def update_parcel_status(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    status: ParcelStatus,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Update parcel status.
    """
    parcel = await ParcelService.update_status(db, id=id, status=status, user_id=current_user.id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel
