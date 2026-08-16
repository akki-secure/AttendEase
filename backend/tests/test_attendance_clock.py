from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.exc import IntegrityError

from app.models.attendance import AttendanceRecord
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
    # 8時間勤務 -> 労基法上の休憩45分が自動付与される
    assert body["break_minutes"] == 45
    assert body["work_minutes"] == 435


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


async def test_duplicate_attendance_record_blocked_by_db_constraint(db_session, employee):
    # 出勤ボタンの連打・二重送信で発生した本番障害の再発防止。
    # アプリ側の事前チェックをすり抜けても、DBのユニーク制約(user_id, date)が最後の砦になることを検証する。
    today = datetime.now(timezone.utc).date()
    db_session.add(AttendanceRecord(user_id=employee.id, date=today, status="PRESENT"))
    await db_session.commit()

    db_session.add(AttendanceRecord(user_id=employee.id, date=today, status="PRESENT"))
    with pytest.raises(IntegrityError):
        await db_session.commit()
