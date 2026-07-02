import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db
from app.core.security import create_access_token, get_password_hash
from app.database import Base
from app.main import app
from app.models.user import User

# 各テストごとにまっさらなインメモリDBを使う（StaticPoolで単一コネクションを共有）
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def _reset_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _create_user(db: AsyncSession, *, employee_id: str, name: str, role: str) -> User:
    user = User(
        employee_id=employee_id,
        name=name,
        email=f"{employee_id}@example.com",
        hashed_password=get_password_hash("Password123!"),
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def employee(db_session: AsyncSession) -> User:
    return await _create_user(db_session, employee_id="E001", name="山田太郎", role="EMPLOYEE")


@pytest_asyncio.fixture
async def other_employee(db_session: AsyncSession) -> User:
    return await _create_user(db_session, employee_id="E002", name="鈴木花子", role="EMPLOYEE")


@pytest_asyncio.fixture
async def manager(db_session: AsyncSession) -> User:
    return await _create_user(db_session, employee_id="M001", name="佐藤上司", role="MANAGER")


def auth_headers(user: User) -> dict[str, str]:
    token = create_access_token(
        {"sub": user.employee_id, "name": user.name, "role": user.role, "user_id": user.id}
    )
    return {"Authorization": f"Bearer {token}"}
