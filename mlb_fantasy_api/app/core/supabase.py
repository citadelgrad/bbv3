import uuid
from dataclasses import dataclass
from functools import lru_cache

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

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


@lru_cache
def get_jwks_client() -> PyJWKClient:
    """Get a cached JWKS client for Supabase token verification."""
    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> SupabaseUser:
    """Validate Supabase JWT and return user information.

    This dependency extracts and validates the JWT token from the
    Authorization header, returning the authenticated user's information.

    Supports both HS256 (symmetric) and ES256 (asymmetric) algorithms.

    Raises:
        HTTPException: If the token is expired, invalid, or missing.
    """
    token = credentials.credentials

    try:
        # First, decode header to check algorithm
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        if alg == "HS256":
            # Symmetric algorithm - use JWT secret
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
        elif alg == "ES256":
            # Asymmetric algorithm - fetch public key from JWKS
            jwks_client = get_jwks_client()
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                audience="authenticated",
            )
        else:
            raise jwt.InvalidTokenError(
                f"Unsupported algorithm '{alg}'. Supported: HS256, ES256."
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
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "AUTH_SERVICE_UNAVAILABLE",
                "message": f"Could not verify token: {e!s}",
            },
        )
