"""
Administrative Account Provisioning Script
==========================================
Usage:
    python scripts/create_admin.py --email admin@university.edu --password SecurePassword123! --name "Platform Administrator"

This script provisions a root administrator account directly via server-side database access,
bypassing public registration endpoints to maintain strict RBAC security.
"""

import sys
import os
import argparse
import asyncio

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.profile import Profile


async def provision_admin(email: str, password: str, full_name: str, phone: str = None, institution: str = None):
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == email.lower()))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"[!] User with email '{email}' already exists.")
            print(f"[*] Upgrading role to ADMINISTRATOR and enabling superuser status...")
            existing_user.role = UserRole.ADMINISTRATOR
            existing_user.is_superuser = True
            existing_user.is_active = True
            if password:
                existing_user.hashed_password = get_password_hash(password)
            await session.commit()
            print(f"[+] User '{email}' successfully updated to ADMINISTRATOR.")
            return

        # Create new Administrator User
        new_admin = User(
            email=email.lower(),
            hashed_password=get_password_hash(password),
            full_name=full_name,
            phone=phone,
            role=UserRole.ADMINISTRATOR,
            is_active=True,
            is_superuser=True
        )
        session.add(new_admin)
        await session.flush()

        # Create linked profile
        new_profile = Profile(
            user_id=new_admin.id,
            institution=institution or "System Administration",
            designation="Platform Administrator",
            department="Governance & IT"
        )
        session.add(new_profile)
        await session.commit()

        print(f"[+] Administrator account successfully provisioned: {email} (ID: {new_admin.id})")

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Provision a Platform Administrator account directly.")
    parser.add_argument("--email", required=True, help="Administrator email address")
    parser.add_argument("--password", required=True, help="Administrator password (min 8 chars)")
    parser.add_argument("--name", default="Platform Administrator", help="Administrator full name")
    parser.add_argument("--phone", default=None, help="Administrator phone number")
    parser.add_argument("--institution", default="System Administration", help="Organization / Institution")

    args = parser.parse_args()

    if len(args.password) < 8:
        print("[!] Error: Password must be at least 8 characters.")
        sys.exit(1)

    asyncio.run(provision_admin(
        email=args.email,
        password=args.password,
        full_name=args.name,
        phone=args.phone,
        institution=args.institution
    ))


if __name__ == "__main__":
    main()
