from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.supabase import SupabaseUser, get_current_user
from app.db.session import get_db
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Get the current authenticated user's profile.

    If the user doesn't have a profile yet (first access after Supabase signup),
    one will be created automatically.
    """
    profile = await user_service.get_or_create_profile(
        db=db,
        supabase_user_id=current_user.id,
        email=current_user.email,
    )
    return UserProfileResponse.model_validate(profile)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    update_data: UserProfileUpdate,
    current_user: SupabaseUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    """Update the current authenticated user's profile."""
    # Ensure profile exists
    await user_service.get_or_create_profile(
        db=db,
        supabase_user_id=current_user.id,
        email=current_user.email,
    )

    profile = await user_service.update_profile(
        db=db,
        supabase_user_id=current_user.id,
        update_data=update_data,
    )
    return UserProfileResponse.model_validate(profile)
