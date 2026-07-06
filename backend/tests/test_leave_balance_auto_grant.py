from datetime import date

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave_balance import LeaveBalance
from app.models.user import User
from tests.conftest import auth_headers


async def test_register_grants_3_days_of_annual_leave(client: AsyncClient, db_session: AsyncSession):
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "employee_id": "E999",
            "name": "新規太郎",
            "password": "Password123!",
        },
    )
    assert res.status_code == 201
    user_id = res.json()["id"]

    balance_result = await db_session.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == date.today().year)
    )
    balance = balance_result.scalar_one()
    assert balance.granted_days == 3
    assert balance.used_days == 0


async def test_admin_created_user_grants_3_days_of_annual_leave(
    client: AsyncClient, db_session: AsyncSession, manager: User
):
    # 管理者権限が必要なので manager を admin に昇格させて利用する
    manager.role = "ADMIN"
    db_session.add(manager)
    await db_session.commit()

    res = await client.post(
        "/api/v1/admin/users",
        json={
            "employee_id": "E998",
            "name": "新規花子",
            "password": "Password123!",
            "role": "EMPLOYEE",
        },
        headers=auth_headers(manager),
    )
    assert res.status_code == 201
    user_id = res.json()["id"]

    balance_result = await db_session.execute(
        select(LeaveBalance).where(LeaveBalance.user_id == user_id, LeaveBalance.year == date.today().year)
    )
    balance = balance_result.scalar_one()
    assert balance.granted_days == 3
    assert balance.used_days == 0
