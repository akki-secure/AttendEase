from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from tests.conftest import auth_headers

_JST = ZoneInfo("Asia/Tokyo")


async def _create_closed_record(client: AsyncClient, employee) -> int:
    headers = auth_headers(employee)
    now = datetime.now(timezone.utc)
    await client.post("/api/v1/attendance/clock-in", json={"clock_in": now.isoformat()}, headers=headers)
    res = await client.post(
        "/api/v1/attendance/clock-out",
        json={"clock_out": (now + timedelta(hours=8)).isoformat()},
        headers=headers,
    )
    return res.json()["id"]


async def test_request_correction_moves_to_pending_and_keeps_original(
    client: AsyncClient, employee
):
    record_id = await _create_closed_record(client, employee)
    now = datetime.now(timezone.utc)

    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": now.isoformat(),
            "clock_out": (now + timedelta(hours=7)).isoformat(),
            "break_minutes": 60,
            "note": "打刻を忘れたため修正します",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "CORRECTION_PENDING"
    assert body["work_minutes"] == 360  # 7h - 60min break


async def test_request_correction_overnight_shift_rolls_to_next_day(
    client: AsyncClient, employee
):
    """退勤時刻が出勤時刻より前（日をまたぐ夜勤）の場合は翌日として扱われる"""
    record_id = await _create_closed_record(client, employee)
    clock_in = datetime(2026, 6, 10, 23, 0, tzinfo=timezone.utc)
    clock_out = datetime(2026, 6, 10, 1, 0, tzinfo=timezone.utc)  # 出勤より前 = 翌日1時のつもり

    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": clock_in.isoformat(),
            "clock_out": clock_out.isoformat(),
            "break_minutes": 0,
            "note": "夜勤のため日をまたぎます",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 200
    body = res.json()
    returned_clock_out = datetime.fromisoformat(body["clock_out"])
    assert returned_clock_out == clock_out + timedelta(days=1)
    assert body["work_minutes"] == 120  # 23:00 -> 翌1:00 = 2時間


async def test_request_correction_equal_times_rejected(client: AsyncClient, employee):
    record_id = await _create_closed_record(client, employee)
    now = datetime.now(timezone.utc)
    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": now.isoformat(),
            "clock_out": now.isoformat(),
            "break_minutes": 0,
            "note": "同時刻",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_request_correction_notifies_managers(
    client: AsyncClient, db_session: AsyncSession, employee, manager
):
    record_id = await _create_closed_record(client, employee)
    now = datetime.now(timezone.utc)
    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": now.isoformat(),
            "clock_out": (now + timedelta(hours=7)).isoformat(),
            "break_minutes": 0,
            "note": "修正申請",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 200

    result = await db_session.execute(
        select(Notification).where(Notification.user_id == manager.id, Notification.type == "CORRECTION_REQUEST")
    )
    notifications = result.scalars().all()
    assert len(notifications) == 1


async def test_request_correction_on_other_users_record_404(
    client: AsyncClient, employee, other_employee
):
    record_id = await _create_closed_record(client, employee)
    now = datetime.now(timezone.utc)
    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": now.isoformat(),
            "clock_out": (now + timedelta(hours=7)).isoformat(),
            "break_minutes": 0,
            "note": "他人の記録を修正しようとする",
        },
        headers=auth_headers(other_employee),
    )
    assert res.status_code == 404


async def _submit_correction(client: AsyncClient, employee, record_id: int) -> None:
    now = datetime.now(timezone.utc)
    res = await client.patch(
        f"/api/v1/attendance/{record_id}/correction-request",
        json={
            "clock_in": now.isoformat(),
            "clock_out": (now + timedelta(hours=7)).isoformat(),
            "break_minutes": 30,
            "note": "修正申請",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 200


async def test_pending_corrections_visible_only_to_manager(
    client: AsyncClient, employee, manager
):
    record_id = await _create_closed_record(client, employee)
    await _submit_correction(client, employee, record_id)

    forbidden = await client.get(
        "/api/v1/attendance/corrections/pending", headers=auth_headers(employee)
    )
    assert forbidden.status_code == 403

    allowed = await client.get(
        "/api/v1/attendance/corrections/pending", headers=auth_headers(manager)
    )
    assert allowed.status_code == 200
    pending = allowed.json()
    assert len(pending) == 1
    assert pending[0]["id"] == record_id
    assert pending[0]["user_name"] == employee.name


async def test_approve_correction_sets_approved_and_reviewer(
    client: AsyncClient, db_session: AsyncSession, employee, manager
):
    record_id = await _create_closed_record(client, employee)
    await _submit_correction(client, employee, record_id)

    res = await client.post(
        f"/api/v1/attendance/corrections/{record_id}/approve",
        json={"comment": "確認しました"},
        headers=auth_headers(manager),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "CORRECTION_APPROVED"
    assert body["reviewer_id"] == manager.id
    assert body["reviewer_comment"] == "確認しました"
    assert body["reviewed_at"] is not None

    result = await db_session.execute(
        select(Notification).where(Notification.user_id == employee.id, Notification.type == "CORRECTION_APPROVED")
    )
    assert len(result.scalars().all()) == 1


async def test_reject_correction_restores_original_values(
    client: AsyncClient, employee, manager
):
    record_id = await _create_closed_record(client, employee)

    before = await client.get(
        "/api/v1/attendance/me?month=" + datetime.now(_JST).strftime("%Y-%m"), headers=auth_headers(employee)
    )
    original = next(r for r in before.json()["records"] if r["id"] == record_id)

    await _submit_correction(client, employee, record_id)

    res = await client.post(
        f"/api/v1/attendance/corrections/{record_id}/reject",
        json={"comment": "内容を確認できません"},
        headers=auth_headers(manager),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "CLOSED"
    assert body["clock_in"] == original["clock_in"]
    assert body["clock_out"] == original["clock_out"]
    assert body["break_minutes"] == original["break_minutes"]


async def test_employee_cannot_approve_correction(client: AsyncClient, employee, other_employee):
    record_id = await _create_closed_record(client, employee)
    await _submit_correction(client, employee, record_id)

    res = await client.post(
        f"/api/v1/attendance/corrections/{record_id}/approve",
        json={},
        headers=auth_headers(other_employee),
    )
    assert res.status_code == 403


async def test_approve_already_approved_correction_conflicts(
    client: AsyncClient, employee, manager
):
    record_id = await _create_closed_record(client, employee)
    await _submit_correction(client, employee, record_id)

    first = await client.post(
        f"/api/v1/attendance/corrections/{record_id}/approve",
        json={},
        headers=auth_headers(manager),
    )
    assert first.status_code == 200

    second = await client.post(
        f"/api/v1/attendance/corrections/{record_id}/approve",
        json={},
        headers=auth_headers(manager),
    )
    assert second.status_code == 409


async def test_approve_nonexistent_record_404(client: AsyncClient, manager):
    res = await client.post(
        "/api/v1/attendance/corrections/9999/approve",
        json={},
        headers=auth_headers(manager),
    )
    assert res.status_code == 404
