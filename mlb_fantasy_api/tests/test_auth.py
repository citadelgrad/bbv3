import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_profile_without_auth(client: AsyncClient):
    """Test that accessing user profile without auth returns 401."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_profile_with_invalid_token(client: AsyncClient):
    """Test that accessing user profile with invalid token returns 401."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTH_TOKEN_INVALID"


@pytest.mark.asyncio
async def test_get_user_profile_with_expired_token(
    client: AsyncClient,
    expired_token: str,
):
    """Test that accessing user profile with expired token returns 401."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTH_TOKEN_EXPIRED"


@pytest.mark.asyncio
async def test_get_user_profile_creates_profile_on_first_access(
    client: AsyncClient,
    valid_token: str,
):
    """Test that a profile is created on first access."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert data["username"] == "test"  # From test@example.com


@pytest.mark.asyncio
async def test_update_user_profile(
    client: AsyncClient,
    valid_token: str,
):
    """Test updating user profile."""
    # First, create the profile
    await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    # Update the profile
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"display_name": "Test User", "username": "new_username"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Test User"
    assert data["username"] == "new_username"


@pytest.mark.asyncio
async def test_update_user_profile_invalid_username(
    client: AsyncClient,
    valid_token: str,
):
    """Test that invalid username format returns 422."""
    # First, create the profile
    await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    # Try to update with invalid username
    response = await client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {valid_token}"},
        json={"username": "invalid username!"},
    )
    assert response.status_code == 422
