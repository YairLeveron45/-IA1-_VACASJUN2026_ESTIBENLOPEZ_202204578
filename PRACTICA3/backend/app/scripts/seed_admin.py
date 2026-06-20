import asyncio

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionFactory
from app.models.user_model import User, UserRole
from app.repositories.user_repository import UserRepository


async def seed_initial_admin() -> None:
    async with SessionFactory() as session:
        repository = UserRepository(session)
        email = settings.initial_admin_email.lower()
        if await repository.get_by_email(email):
            print(f"Initial administrator already exists: {email}")
            return

        admin = User(
            name=settings.initial_admin_name,
            email=email,
            password_hash=hash_password(settings.initial_admin_password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        await repository.create(admin)
        print(f"Initial administrator created: {email}")


if __name__ == "__main__":
    asyncio.run(seed_initial_admin())
