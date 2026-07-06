from datetime import date

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_balance import LeaveBalance
from app.models.notification import Notification
from tests.conftest import auth_headers


async def _create_late_request(client: AsyncClient, employee, *, leave_type: str = "LATE") -> dict:
    today = date.today().isoformat()
    res = await client.post(
        "/api/v1/leaves",
        json={
            "leave_type": leave_type,
            "start_date": today,
            "end_date": today,
            "scheduled_time": "10:30:00",
            "reason": "電車遅延のため",
        },
        headers=auth_headers(employee),
    )
    return res


async def test_create_late_request_succeeds(client: AsyncClient, employee):
    res = await _create_late_request(client, employee, leave_type="LATE")
    assert res.status_code == 201
    body = res.json()
    assert body["leave_type"] == "LATE"
    assert body["days"] == 1
    assert body["scheduled_time"] == "10:30:00"


async def test_create_early_leave_request_succeeds(client: AsyncClient, employee):
    res = await _create_late_request(client, employee, leave_type="EARLY_LEAVE")
    assert res.status_code == 201
    body = res.json()
    assert body["leave_type"] == "EARLY_LEAVE"
    assert body["scheduled_time"] == "10:30:00"


async def test_late_request_with_different_dates_rejected(client: AsyncClient, employee):
    today = date.today().isoformat()
    res = await client.post(
        "/api/v1/leaves",
        json={
            "leave_type": "LATE",
            "start_date": today,
            "end_date": "2099-01-01",
            "scheduled_time": "10:30:00",
            "reason": "電車遅延のため",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_late_request_without_scheduled_time_rejected(client: AsyncClient, employee):
    today = date.today().isoformat()
    res = await client.post(
        "/api/v1/leaves",
        json={
            "leave_type": "LATE",
            "start_date": today,
            "end_date": today,
            "reason": "電車遅延のため",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_annual_request_with_scheduled_time_rejected(client: AsyncClient, employee):
    today = date.today().isoformat()
    res = await client.post(
        "/api/v1/leaves",
        json={
            "leave_type": "ANNUAL",
            "start_date": today,
            "end_date": today,
            "scheduled_time": "10:30:00",
            "reason": "私用のため",
        },
        headers=auth_headers(employee),
    )
    assert res.status_code == 422


async def test_approve_late_request_does_not_touch_leave_balance(
    client: AsyncClient, db_session: AsyncSession, employee, manager
):
    res = await _create_late_request(client, employee, leave_type="LATE")
    leave_id = res.json()["id"]

    approve_res = await client.post(
        f"/api/v1/leaves/{leave_id}/approve",
        json={"comment": "確認しました"},
        headers=auth_headers(manager),
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    result = await db_session.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == employee.id)
    )
    assert result.scalar_one_or_none() is None


async def test_late_request_appears_in_pending_list_and_can_be_rejected(
    client: AsyncClient, employee, manager
):
    res = await _create_late_request(client, employee, leave_type="EARLY_LEAVE")
    leave_id = res.json()["id"]

    pending = await client.get("/api/v1/leaves/pending", headers=auth_headers(manager))
    assert pending.status_code == 200
    assert any(r["id"] == leave_id for r in pending.json())

    reject_res = await client.post(
        f"/api/v1/leaves/{leave_id}/reject",
        json={"comment": "詳細を確認できません"},
        headers=auth_headers(manager),
    )
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "REJECTED"


async def test_create_late_request_notifies_managers_with_label(
    client: AsyncClient, db_session: AsyncSession, employee, manager
):
    res = await _create_late_request(client, employee, leave_type="LATE")
    assert res.status_code == 201

    result = await db_session.execute(
        select(Notification).where(Notification.user_id == manager.id, Notification.type == "LEAVE_REQUEST")
    )
    notifications = result.scalars().all()
    assert len(notifications) == 1
    assert "遅刻" in notifications[0].message
