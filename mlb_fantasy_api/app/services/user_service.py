import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import logger
from app.models.user_profile import UserProfile
from app.schemas.user import UserProfileUpdate


async def get_profile_by_supabase_id(
    db: AsyncSession,
    supabase_user_id: uuid.UUID,
) -> UserProfile | None:
    """Get a user profile by Supabase user ID."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.supabase_user_id == supabase_user_id)
    )
    return result.scalar_one_or_none()


async def get_or_create_profile(
    db: AsyncSession,
    supabase_user_id: uuid.UUID,
    email: str | None = None,
) -> UserProfile:
    """Get existing profile or create one for new users.

    This is called when a user first accesses the API after signing up
    via Supabase. A default username is generated from the email.
    """
    profile = await get_profile_by_supabase_id(db, supabase_user_id)

    if profile:
        return profile

    # Generate default username from email or UUID
    if email:
        default_username = email.split("@")[0][:30]
    else:
        default_username = f"user_{str(supabase_user_id)[:8]}"

    # Ensure username is unique by appending random suffix if needed
    username = await _ensure_unique_username(db, default_username)

    profile = UserProfile(
        supabase_user_id=supabase_user_id,
        username=username,
        display_name=None,
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    logger.info(
        "Created user profile",
        supabase_user_id=str(supabase_user_id),
        username=username,
    )

    return profile


async def update_profile(
    db: AsyncSession,
    supabase_user_id: uuid.UUID,
    update_data: UserProfileUpdate,
) -> UserProfile:
    """Update a user's profile."""
    profile = await get_profile_by_supabase_id(db, supabase_user_id)

    if not profile:
        raise NotFoundError(resource="User profile")

    update_dict = update_data.model_dump(exclude_unset=True)

    if not update_dict:
        return profile

    try:
        for field, value in update_dict.items():
            setattr(profile, field, value)

        await db.commit()
        await db.refresh(profile)

        logger.info(
            "Updated user profile",
            supabase_user_id=str(supabase_user_id),
            updated_fields=list(update_dict.keys()),
        )

        return profile
    except IntegrityError as e:
        await db.rollback()
        if "username" in str(e):
            raise ValidationError(
                message="Username already taken",
                details={"field": "username"},
            )
        raise


async def _ensure_unique_username(db: AsyncSession, base_username: str) -> str:
    """Ensure the username is unique, appending a suffix if needed."""
    # Sanitize username to only allow alphanumeric and underscores
    sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in base_username)
    sanitized = sanitized[:30] or "user"

    username = sanitized
    suffix = 1

    while True:
        result = await db.execute(
            select(UserProfile).where(UserProfile.username == username)
        )
        if result.scalar_one_or_none() is None:
            return username

        # Add numeric suffix
        username = f"{sanitized[:26]}_{suffix}"
        suffix += 1

        if suffix > 1000:
            # Fallback to UUID-based username
            return f"user_{uuid.uuid4().hex[:8]}"
