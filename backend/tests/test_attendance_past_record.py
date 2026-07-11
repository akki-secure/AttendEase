from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from httpx import AsyncClient

from tests.conftest import auth_headers


def _jst_today():
    return datetime.now(ZoneInfo("Asia/Tokyo")).date()


def _yesterday_within_month():
    """月初(1日)にテストを実行すると当月内に過去日付が作れないためスキップする"""
    today = _jst_today()
    if today.day <= 1:
        pytest.skip("月初は当月内の過去日付が存在しないため実行不可")
    return today - timedelta(days=1)


async def test_create_past_record_success(client: AsyncClient, employee):
    target_date = _yesterday_within_month()
    clock_in = datetime(target_date.year, target_date.month, target_date.day, 0, 0, tzinfo=timezone.utc)
    res = await client.post(
        "/api/v1/attendance/record",
        json={
            "date": target_date.isoformat(),
            "clock_in": clock_in.isoformat(),
            "clock_out": (clock_in + timedelta(hours=8)).isoformat(),
            "break_minutes": 60,
            "work_type": "office",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "CLOSED"
    assert body["work_minutes"] == 420


async def test_create_past_record_future_date_rejected(client: AsyncClient, employee):
    today = _jst_today()
    future = today + timedelta(days=1)
    clock_in = datetime(future.year, future.month, future.day, 9, 0, tzinfo=timezone.utc)
    res = await client.post(
        "/api/v1/attendance/record",
        json={
            "date": future.isoformat(),
            "clock_in": clock_in.isoformat(),
            "clock_out": (clock_in + timedelta(hours=8)).isoformat(),
            "work_type": "office",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_create_past_record_clock_out_before_clock_in_rejected(client: AsyncClient, employee):
    target_date = _yesterday_within_month()
    clock_in = datetime(target_date.year, target_date.month, target_date.day, 9, 0, tzinfo=timezone.utc)
    res = await client.post(
        "/api/v1/attendance/record",
        json={
            "date": target_date.isoformat(),
            "clock_in": clock_in.isoformat(),
            "clock_out": (clock_in - timedelta(hours=1)).isoformat(),
            "work_type": "office",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_create_past_record_duplicate_conflicts(client: AsyncClient, employee):
    target_date = _yesterday_within_month()
    clock_in = datetime(target_date.year, target_date.month, target_date.day, 9, 0, tzinfo=timezone.utc)
    payload = {
        "date": target_date.isoformat(),
        "clock_in": clock_in.isoformat(),
        "clock_out": (clock_in + timedelta(hours=8)).isoformat(),
        "work_type": "office",
    }
    headers = auth_headers(employee)
    first = await client.post("/api/v1/attendance/record", json=payload, headers=headers)
    assert first.status_code == 201

    second = await client.post("/api/v1/attendance/record", json=payload, headers=headers)
    assert second.status_code == 409
