from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider_model import Provider


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self, offset: int, limit: int) -> tuple[list[Provider], int]:
        items_result = await self.session.execute(
            select(Provider).order_by(Provider.id).offset(offset).limit(limit)
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(Provider)
        )
        return list(items_result.scalars().all()), total_result.scalar_one()

    async def get_by_id(self, provider_id: int) -> Provider | None:
        return await self.session.get(Provider, provider_id)

    async def get_by_nit(self, nit: str) -> Provider | None:
        result = await self.session.execute(
            select(Provider).where(Provider.nit == nit)
        )
        return result.scalar_one_or_none()

    async def create(self, provider: Provider) -> Provider:
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def create_pending(self, provider: Provider) -> Provider:
        self.session.add(provider)
        await self.session.flush()
        return provider

    async def update(self, provider: Provider) -> Provider:
        await self.session.commit()
        await self.session.refresh(provider)
        return provider
