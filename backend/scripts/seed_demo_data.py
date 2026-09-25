"""
Seed Demo Publications Script
=============================
Seeds realistic deep-tech publications with multi-sentence scientific abstracts
into the database to enable live Module 3 paper analysis verification.

Usage:
    py -3.10 scripts/seed_demo_data.py
"""

import sys
import os
import asyncio
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.models.user import User
from app.models.profile import Profile
from app.models.publication import Publication, PublicationKeyword, profile_publications
from app.services.providers.mock_provider import SAMPLE_PUBLICATIONS


async def seed_publications(db_url: str = None):
    target_url = db_url or os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///research_intel.db"
    # If settings.DATABASE_URL is postgres and localhost is refused, try sqlite
    print(f"[*] Connecting to database: {target_url}")
    
    connect_args = {"check_same_thread": False} if "sqlite" in target_url else {}
    engine = create_async_engine(target_url, echo=False, connect_args=connect_args)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with engine.begin() as conn:
            from app.core.database import Base
            # Import all models to ensure metadata is complete
            from app.models.user import User, UserRole
            from app.models.profile import Profile
            from app.models.publication import Publication, PublicationKeyword, profile_publications
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"[!] Table creation failed or skipped: {e}")

    async with session_factory() as session:
        # Fetch or create a default user to link publications to
        user_res = await session.execute(select(User).order_by(User.id.asc()))
        user = user_res.scalars().first()
        if not user:
            from app.core.security import get_password_hash
            print("[*] Creating default researcher user for demo...")
            user = User(
                email="test.researcher@example.com",
                hashed_password=get_password_hash("ResearcherPass123!"),
                full_name="Dr. Jane Doe",
                role=UserRole.RESEARCHER,
                is_active=True,
                is_superuser=False
            )
            session.add(user)
            await session.flush()

        profile_res = await session.execute(select(Profile).where(Profile.user_id == user.id))
        profile = profile_res.scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user.id, institution="National Science Foundation", designation="Principal Investigator")
            session.add(profile)
            await session.flush()
            await session.refresh(profile)

        print(f"[*] Seeding demo publications for User ID {user.id} ({user.email})...")

        for sample in SAMPLE_PUBLICATIONS:
            # Check if publication exists by DOI
            pub_res = await session.execute(
                select(Publication).where(Publication.doi == sample["doi"])
            )
            existing = pub_res.scalar_one_or_none()

            if existing:
                print(f"[-] Publication already exists: ID {existing.id} - '{existing.title[:45]}...'")
                # Update abstract with enriched version if it was the old short abstract
                existing.abstract = sample["abstract"]
                await session.flush()
                continue

            new_pub = Publication(
                title=sample["title"],
                authors=sample["authors"],
                abstract=sample["abstract"],
                publication_date=sample["publication_date"],
                venue=sample["venue"],
                doi=sample["doi"],
                citation_count=sample["citation_count"],
                primary_domain=sample["primary_domain"],
                source="openalex_mock",
                external_id=sample["external_id"],
                url=sample["url"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(new_pub)
            await session.flush()

            # Add keywords
            for kw in sample["keywords"]:
                session.add(PublicationKeyword(publication_id=new_pub.id, keyword=kw))

            # Associate with profile
            await session.execute(
                profile_publications.insert().values(
                    profile_id=profile.id,
                    publication_id=new_pub.id,
                    is_primary_author=True,
                    created_at=datetime.now(timezone.utc),
                )
            )
            print(f"[+] Seeded publication ID {new_pub.id}: '{new_pub.title}'")

        await session.commit()
        print("[+] Seeding completed successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_publications())
