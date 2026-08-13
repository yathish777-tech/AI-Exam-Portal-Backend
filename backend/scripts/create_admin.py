import asyncio
import getpass

from app.core.security import hash_password
from app.database.session import AsyncSessionLocal
from app.models.user import User
from app.repositories.role_repository import RoleRepository


async def create_admin():
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password: ")

    async with AsyncSessionLocal() as db:
        roles = RoleRepository(db)
        role = await roles.get_by_name("ADMIN")

        if role is None:
            print("ERROR: ADMIN role does not exist.")
            return

        # Check whether email already exists
        from app.repositories.user_repository import UserRepository

        users = UserRepository(db)
        existing = await users.get_by_email(email)

        if existing:
            print("ERROR: This email already exists.")
            print(f"Existing user ID: {existing.id}")
            return

        password_hash = hash_password(password)

        user = await users.create(
            email=email,
            password_hash=password_hash,
            role_id=role.id,
        )

        await db.commit()

        print("\nAdmin created successfully!")
        print(f"Email: {email}")
        print(f"User ID: {user.id}")
        print("Role: ADMIN")


if __name__ == "__main__":
    asyncio.run(create_admin())