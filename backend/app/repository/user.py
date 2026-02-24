from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.models import User


class UserRepository:
    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, username: str, password: str) -> User:
        user = User(username=username, hashed_password=get_password_hash(password), is_active=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def ensure_default_admin(self, db: AsyncSession, username: str, password: str) -> User:
        user = await self.get_by_username(db, username)
        if user:
            return user
        return await self.create(db, username, password)
