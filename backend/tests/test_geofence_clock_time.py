from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.geofence_setting import GeofenceSetting
from app.models.office_location import OfficeLocation
from tests.conftest import auth_headers

_OFFICE_LAT = 35.681236
_OFFICE_LON = 139.767125


async def _enable_geofence_with_office(db: AsyncSession) -> None:
    db.add(GeofenceSetting(enabled=True))
    db.add(
        OfficeLocation(
            name="本社",
            latitude=_OFFICE_LAT,
            longitude=_OFFICE_LON,
            radius_meters=200,
            is_active=True,
        )
    )
    await db.commit()


async def test_clock_in_ignores_manual_time_when_geofence_enabled(
    client: AsyncClient, db_session: AsyncSession, employee
):
    """ジオフェンスON時は、拠点内からでも自己申告の出勤時刻は無視されサーバー時刻が使われる"""
    await _enable_geofence_with_office(db_session)

    spoofed_clock_in = datetime.now(timezone.utc) - timedelta(hours=2)
    before = datetime.now(timezone.utc)
    res = await client.post(
        "/api/v1/attendance/clock-in",
        json={
            "clock_in": spoofed_clock_in.isoformat(),
            "latitude": _OFFICE_LAT,
            "longitude": _OFFICE_LON,
        },
        headers=auth_headers(employee),
    )
    after = datetime.now(timezone.utc)

    assert res.status_code == 201
    body = res.json()
    actual_clock_in = datetime.fromisoformat(body["clock_in"])
    assert before <= actual_clock_in <= after  # 申告した2時間前ではなく、実際に打刻した瞬間の時刻になる


async def test_clock_out_ignores_manual_time_when_geofence_enabled(
    client: AsyncClient, db_session: AsyncSession, employee
):
    """ジオフェンスON時は、自己申告の退勤時刻も無視されサーバー時刻が使われる"""
    await _enable_geofence_with_office(db_session)

    await client.post(
        "/api/v1/attendance/clock-in",
        json={"latitude": _OFFICE_LAT, "longitude": _OFFICE_LON},
        headers=auth_headers(employee),
    )

    spoofed_clock_out = datetime.now(timezone.utc) + timedelta(hours=3)
    before = datetime.now(timezone.utc)
    res = await client.post(
        "/api/v1/attendance/clock-out",
        json={
            "clock_out": spoofed_clock_out.isoformat(),
            "latitude": _OFFICE_LAT,
            "longitude": _OFFICE_LON,
        },
        headers=auth_headers(employee),
    )
    after = datetime.now(timezone.utc)

    assert res.status_code == 200
    body = res.json()
    actual_clock_out = datetime.fromisoformat(body["clock_out"])
    assert before <= actual_clock_out <= after  # 申告した3時間後ではなく、実際に打刻した瞬間の時刻になる


async def test_clock_in_allows_manual_time_when_geofence_disabled(
    client: AsyncClient, employee
):
    """ジオフェンスOFF時は、これまで通り自己申告の出勤時刻がそのまま使われる"""
    manual_clock_in = datetime.now(timezone.utc) - timedelta(hours=1)
    res = await client.post(
        "/api/v1/attendance/clock-in",
        json={"clock_in": manual_clock_in.isoformat()},
        headers=auth_headers(employee),
    )
    assert res.status_code == 201
    body = res.json()
    assert datetime.fromisoformat(body["clock_in"]) == manual_clock_in
