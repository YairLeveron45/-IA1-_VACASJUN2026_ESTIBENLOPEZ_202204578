from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def list(self, offset: int, limit: int) -> tuple[list[User], int]:
        items_result = await self.session.execute(
            select(User).order_by(User.id).offset(offset).limit(limit)
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(User)
        )
        return list(items_result.scalars().all()), total_result.scalar_one()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        await self.session.commit()
        await self.session.refresh(user)
        return user
