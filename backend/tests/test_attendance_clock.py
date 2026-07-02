from datetime import datetime, timedelta, timezone

from httpx import AsyncClient

from tests.conftest import auth_headers


async def test_clock_in_creates_present_record(client: AsyncClient, employee):
    res = await client.post(
        "/api/v1/attendance/clock-in",
        json={"work_type": "office"},
        headers=auth_headers(employee),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "PRESENT"
    assert body["work_type"] == "office"
    assert body["clock_out"] is None


async def test_clock_in_twice_conflicts(client: AsyncClient, employee):
    headers = auth_headers(employee)
    first = await client.post("/api/v1/attendance/clock-in", json={}, headers=headers)
    assert first.status_code == 201

    second = await client.post("/api/v1/attendance/clock-in", json={}, headers=headers)
    assert second.status_code == 409


async def test_clock_out_without_clock_in_fails(client: AsyncClient, employee):
    res = await client.post("/api/v1/attendance/clock-out", json={}, headers=auth_headers(employee))
    assert res.status_code == 400


async def test_clock_out_after_clock_in_succeeds(client: AsyncClient, employee):
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/attendance/clock-in",
        json={"clock_in": now.isoformat()},
        headers=headers,
    )
    res = await client.post(
        "/api/v1/attendance/clock-out",
        json={"clock_out": (now + timedelta(hours=8)).isoformat()},
        headers=headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "CLOSED"
    assert body["work_minutes"] == 480


async def test_clock_out_before_clock_in_rejected(client: AsyncClient, employee):
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)
    await client.post(
        "/api/v1/attendance/clock-in",
        json={"clock_in": now.isoformat()},
        headers=headers,
    )
    res = await client.post(
        "/api/v1/attendance/clock-out",
        json={"clock_out": (now - timedelta(hours=1)).isoformat()},
        headers=headers,
    )
    assert res.status_code == 422


async def test_clock_out_twice_conflicts(client: AsyncClient, employee):
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)
    await client.post("/api/v1/attendance/clock-in", json={"clock_in": now.isoformat()}, headers=headers)
    await client.post(
        "/api/v1/attendance/clock-out",
        json={"clock_out": (now + timedelta(hours=8)).isoformat()},
        headers=headers,
    )
    res = await client.post(
        "/api/v1/attendance/clock-out",
        json={"clock_out": (now + timedelta(hours=9)).isoformat()},
        headers=headers,
    )
    assert res.status_code == 409


async def test_unauthenticated_request_rejected(client: AsyncClient):
    res = await client.get("/api/v1/attendance/today")
    assert res.status_code in (401, 403)
