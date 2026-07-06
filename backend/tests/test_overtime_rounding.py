from datetime import datetime, timedelta, timezone

from httpx import AsyncClient

from tests.conftest import auth_headers


async def test_overtime_is_rounded_down_to_15_minutes(client: AsyncClient, employee):
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)

    await client.post(
        "/api/v1/attendance/clock-in",
        json={"clock_in": now.isoformat()},
        headers=headers,
    )
    res = await client.post(
        "/api/v1/attendance/clock-out",
        # 実働8時間40分 -> 残業40分 -> 15分単位切り捨てで30分
        json={"clock_out": (now + timedelta(hours=8, minutes=40)).isoformat()},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()["work_minutes"] == 520

    month = now.strftime("%Y-%m")
    monthly = await client.get(f"/api/v1/attendance/me?month={month}", headers=headers)
    assert monthly.status_code == 200
    assert monthly.json()["total_overtime_minutes"] == 30


async def test_overtime_under_15_minutes_rounds_to_zero(client: AsyncClient, employee):
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)

    await client.post(
        "/api/v1/attendance/clock-in",
        json={"clock_in": now.isoformat()},
        headers=headers,
    )
    await client.post(
        "/api/v1/attendance/clock-out",
        # 実働8時間10分 -> 残業10分 -> 15分未満なので0分
        json={"clock_out": (now + timedelta(hours=8, minutes=10)).isoformat()},
        headers=headers,
    )

    month = now.strftime("%Y-%m")
    monthly = await client.get(f"/api/v1/attendance/me?month={month}", headers=headers)
    assert monthly.status_code == 200
    assert monthly.json()["total_overtime_minutes"] == 0
