from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.models.research_domain import (
    ResearchDomain,
    ResearchInterest,
    ProfileKeyword,
    TechnologyArea
)
from app.models.academic_history import AcademicHistory, ResearchHistory
from app.schemas.research_profile import ExtendedProfileUpdate
from app.core.exceptions import EntityNotFoundException


DEFAULT_RESEARCH_DOMAINS = [
    {"name": "Artificial Intelligence & Machine Learning", "description": "Deep learning, neural architectures, computer vision, and NLP"},
    {"name": "Biotechnology & Genomic Sciences", "description": "CRISPR, gene therapies, synthetic biology, and bioprocessing"},
    {"name": "Quantum Technologies", "description": "Quantum computing, quantum cryptography, and quantum sensing"},
    {"name": "Clean Energy & Sustainability", "description": "Solid-state batteries, hydrogen fuel cells, and carbon capture"},
    {"name": "Advanced Materials & Nanotechnology", "description": "Metamaterials, 2D materials, graphene, and high-entropy alloys"},
    {"name": "Robotics & Autonomous Systems", "description": "Control theory, soft robotics, autonomous vehicles, and swarm intelligence"},
    {"name": "Healthcare & Translational Medicine", "description": "Precision diagnostics, digital health, and immunotherapy"},
    {"name": "Cybersecurity & Cryptography", "description": "Post-quantum cryptography, Zero Trust architectures, and hardware security"}
]


class ProfileService:
    @staticmethod
    async def seed_default_domains_if_empty(db: AsyncSession) -> None:
        """Seeds default taxonomy domains if none exist in the database."""
        result = await db.execute(select(ResearchDomain))
        existing = result.scalars().all()
        if not existing:
            for domain_data in DEFAULT_RESEARCH_DOMAINS:
                domain = ResearchDomain(
                    name=domain_data["name"],
                    description=domain_data["description"]
                )
                db.add(domain)
            await db.flush()

    @staticmethod
    async def get_all_domains(db: AsyncSession) -> List[ResearchDomain]:
        """Retrieves all standard research domains."""
        await ProfileService.seed_default_domains_if_empty(db)
        result = await db.execute(select(ResearchDomain).order_by(ResearchDomain.name))
        return list(result.scalars().all())

    @staticmethod
    async def get_or_create_profile(user_id: int, db: AsyncSession) -> Profile:
        """Retrieves or initializes a base profile for the given user."""
        result = await db.execute(
            select(Profile)
            .where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = Profile(user_id=user_id)
            db.add(profile)
            await db.flush()
            await db.refresh(profile)
        return profile

    @staticmethod
    async def get_extended_profile(user_id: int, db: AsyncSession) -> Profile:
        """Retrieves full extended profile with all normalized child entities pre-loaded."""
        # Ensure base profile exists
        await ProfileService.get_or_create_profile(user_id, db)

        result = await db.execute(
            select(Profile)
            .options(
                selectinload(Profile.domains),
                selectinload(Profile.interests),
                selectinload(Profile.keywords),
                selectinload(Profile.technology_areas),
                selectinload(Profile.academic_histories),
                selectinload(Profile.research_histories),
            )
            .where(Profile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise EntityNotFoundException(message="Profile not found")
        return profile

    @staticmethod
    async def update_extended_profile(
        user_id: int,
        update_in: ExtendedProfileUpdate,
        db: AsyncSession
    ) -> Profile:
        """Updates user profile information and synchronizes all normalized child collections."""
        profile = await ProfileService.get_extended_profile(user_id, db)

        # 1. Update Top-level profile metadata
        if update_in.institution is not None:
            profile.institution = update_in.institution
        if update_in.department is not None:
            profile.department = update_in.department
        if update_in.bio is not None:
            profile.bio = update_in.bio
        if update_in.orcid_id is not None:
            profile.orcid_id = update_in.orcid_id
        if update_in.website is not None:
            profile.website = update_in.website

        # 2. Synchronize Research Domains (Many-to-Many)
        if update_in.domain_ids is not None:
            domain_result = await db.execute(
                select(ResearchDomain).where(ResearchDomain.id.in_(update_in.domain_ids))
            )
            selected_domains = list(domain_result.scalars().all())
            profile.domains = selected_domains

        # 3. Synchronize Research Interests (1-to-Many replacement)
        if update_in.interests is not None:
            profile.interests.clear()
            for item in update_in.interests:
                profile.interests.append(
                    ResearchInterest(
                        profile_id=profile.id,
                        title=item.title,
                        description=item.description,
                        importance_level=item.importance_level
                    )
                )

        # 4. Synchronize Keywords (1-to-Many replacement)
        if update_in.keywords is not None:
            profile.keywords.clear()
            # Deduplicate keywords case-insensitively
            seen = set()
            for kw in update_in.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen:
                    seen.add(clean_kw.lower())
                    profile.keywords.append(
                        ProfileKeyword(profile_id=profile.id, keyword=clean_kw)
                    )

        # 5. Synchronize Technology Areas
        if update_in.technology_areas is not None:
            profile.technology_areas.clear()
            for tech in update_in.technology_areas:
                profile.technology_areas.append(
                    TechnologyArea(
                        profile_id=profile.id,
                        name=tech.name,
                        description=tech.description
                    )
                )

        # 6. Synchronize Academic Histories
        if update_in.academic_histories is not None:
            profile.academic_histories.clear()
            for acad in update_in.academic_histories:
                profile.academic_histories.append(
                    AcademicHistory(
                        profile_id=profile.id,
                        degree=acad.degree,
                        field_of_study=acad.field_of_study,
                        institution=acad.institution,
                        start_year=acad.start_year,
                        end_year=acad.end_year
                    )
                )

        # 7. Synchronize Research Histories
        if update_in.research_histories is not None:
            profile.research_histories.clear()
            for res in update_in.research_histories:
                profile.research_histories.append(
                    ResearchHistory(
                        profile_id=profile.id,
                        project_title=res.project_title,
                        role=res.role,
                        organization=res.organization,
                        start_date=res.start_date,
                        end_date=res.end_date,
                        description=res.description
                    )
                )

        await db.flush()
        await db.refresh(profile)
        return await ProfileService.get_extended_profile(user_id, db)
