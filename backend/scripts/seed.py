"""テストユーザーを投入するシードスクリプト

実行方法:
    docker compose exec backend python -m scripts.seed
"""
import asyncio

from sqlalchemy import select

from app.core.security import get_password_hash
from app.database import AsyncSessionLocal
from app.models.user import User

TEST_USERS = [
    {"employee_id": "EMP001", "name": "山田 太郎", "password": "Password1!", "role": "EMPLOYEE"},
    {"employee_id": "EMP002", "name": "鈴木 花子", "password": "Password1!", "role": "MANAGER"},
    {"employee_id": "ADMIN001", "name": "システム管理者", "password": "Admin1234!", "role": "ADMIN"},
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for data in TEST_USERS:
            result = await db.execute(select(User).where(User.employee_id == data["employee_id"]))
            if result.scalar_one_or_none() is not None:
                print(f"スキップ: {data['employee_id']} は既に存在します")
                continue

            user = User(
                employee_id=data["employee_id"],
                name=data["name"],
                hashed_password=get_password_hash(data["password"]),
                role=data["role"],
            )
            db.add(user)
            print(f"作成: {data['employee_id']} ({data['name']})")

        await db.commit()
    print("シード完了")


if __name__ == "__main__":
    asyncio.run(seed())
