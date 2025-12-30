import uuid
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

security = HTTPBearer()


@dataclass
class SupabaseUser:
    """Represents the authenticated user from Supabase JWT."""

    id: uuid.UUID
    email: str | None
    role: str
    app_metadata: dict
    user_metadata: dict

    @classmethod
    def from_jwt_payload(cls, payload: dict) -> "SupabaseUser":
        """Create a SupabaseUser from JWT payload."""
        return cls(
            id=uuid.UUID(payload["sub"]),
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
            app_metadata=payload.get("app_metadata", {}),
            user_metadata=payload.get("user_metadata", {}),
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> SupabaseUser:
    """Validate Supabase JWT and return user information.

    This dependency extracts and validates the JWT token from the
    Authorization header, returning the authenticated user's information.

    Raises:
        HTTPException: If the token is expired, invalid, or missing.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return SupabaseUser.from_jwt_payload(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_EXPIRED",
                "message": "Token has expired",
            },
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_INVALID",
                "message": "Invalid token audience",
            },
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "AUTH_TOKEN_INVALID",
                "message": f"Invalid token: {e!s}",
            },
        )
