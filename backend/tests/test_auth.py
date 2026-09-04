import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@personalix.os",
            "password": "Password123!",
            "full_name": "New Tester",
        },
    )

    assert reg_resp.status_code == 201

    data = reg_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    dup_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@personalix.os",
            "password": "Password123!",
            "full_name": "New Tester",
        },
    )

    assert dup_resp.status_code == 409

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@personalix.os",
            "password": "Password123!",
        },
    )

    assert login_resp.status_code == 200

    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "newuser@personalix.os"
    assert me_resp.json()["full_name"] == "New Tester"


@pytest.mark.asyncio
async def test_demo_login(client: AsyncClient):
    resp = await client.post("/api/v1/auth/demo-login")

    assert resp.status_code == 200
    assert "access_token" in resp.json()