from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.funding import FundingOpportunity, FundingKeyword, funding_opportunity_domains
from app.models.research_domain import ResearchDomain
from app.schemas.funding import (
    FundingIngestRequest,
    FundingIngestResponse,
    FundingOpportunityRead,
)
from app.services.providers.funding_base import NormalizedFundingOpportunity
from app.services.providers.funding_providers import funding_provider_service
from app.services.providers.base import (
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.services.funding_service import FundingService
from app.core.exceptions import (
    EntityNotFoundException,
    CustomAPIException,
    DuplicateEntityException,
    PermissionDeniedException,
)


class FundingIngestService:
    @staticmethod
    def validate_normalized_opportunity(norm: NormalizedFundingOpportunity) -> NormalizedFundingOpportunity:
        """Validates normalized funding opportunity fields before database persistence."""
        if not norm.title or len(norm.title.strip()) < 3:
            raise CustomAPIException(
                status_code=422,
                code="VALIDATION_ERROR",
                message="Normalized funding opportunity title is missing or too short (min 3 chars)"
            )
        if not norm.funding_agency or len(norm.funding_agency.strip()) < 2:
            raise CustomAPIException(
                status_code=422,
                code="VALIDATION_ERROR",
                message="Funding agency name is required"
            )
        if norm.funding_amount is not None and norm.funding_amount < 0:
            norm.funding_amount = None

        if not norm.currency:
            norm.currency = "USD"

        return norm

    @staticmethod
    async def persist_normalized_opportunity(
        user_id: int,
        norm_opp: NormalizedFundingOpportunity,
        db: AsyncSession
    ) -> Tuple[FundingOpportunity, str]:
        """
        Deduplicates against existing database records (by source + external_id, or normalized URL),
        enriches metadata on existing records, persists new opportunities, and links domain taxonomies and keywords.
        Returns: (FundingOpportunity, status: "inserted" | "updated")
        """
        norm_opp = FundingIngestService.validate_normalized_opportunity(norm_opp)

        # 1. Deduplication by source + external_id
        existing_opp: Optional[FundingOpportunity] = None
        if norm_opp.external_id and norm_opp.source != "manual":
            dup_res = await db.execute(
                select(FundingOpportunity).where(
                    and_(
                        FundingOpportunity.source == norm_opp.source,
                        FundingOpportunity.external_id == norm_opp.external_id
                    )
                )
            )
            existing_opp = dup_res.scalar_one_or_none()

        # 2. Deduplication by normalized URL
        if not existing_opp and norm_opp.url:
            clean_url = norm_opp.url.strip().lower()
            url_res = await db.execute(
                select(FundingOpportunity).where(func.lower(FundingOpportunity.url) == clean_url)
            )
            existing_opp = url_res.scalar_one_or_none()

        if existing_opp:
            # Metadata enrichment
            if norm_opp.description and (not existing_opp.description or len(norm_opp.description) > len(existing_opp.description)):
                existing_opp.description = norm_opp.description
            if norm_opp.funding_amount and not existing_opp.funding_amount:
                existing_opp.funding_amount = norm_opp.funding_amount
            if norm_opp.application_deadline and not existing_opp.application_deadline:
                existing_opp.application_deadline = norm_opp.application_deadline
            if norm_opp.eligibility_summary and not existing_opp.eligibility_summary:
                existing_opp.eligibility_summary = norm_opp.eligibility_summary
            if norm_opp.status and norm_opp.status != existing_opp.status:
                existing_opp.status = norm_opp.status

            # Domain linkage enrichment
            if norm_opp.domain_names:
                for d_name in norm_opp.domain_names:
                    clean_d = d_name.strip()
                    if not clean_d:
                        continue
                    d_res = await db.execute(
                        select(ResearchDomain).where(func.lower(ResearchDomain.name) == clean_d.lower())
                    )
                    domain_obj = d_res.scalar_one_or_none()
                    if not domain_obj:
                        domain_obj = ResearchDomain(name=clean_d, description=f"{clean_d} research domain")
                        db.add(domain_obj)
                        await db.flush()

                    assoc_check = await db.execute(
                        select(funding_opportunity_domains).where(
                            and_(
                                funding_opportunity_domains.c.funding_opportunity_id == existing_opp.id,
                                funding_opportunity_domains.c.domain_id == domain_obj.id
                            )
                        )
                    )
                    if not assoc_check.first():
                        await db.execute(
                            funding_opportunity_domains.insert().values(
                                funding_opportunity_id=existing_opp.id,
                                domain_id=domain_obj.id
                            )
                        )

            # Keyword enrichment
            if norm_opp.keywords:
                kw_res = await db.execute(
                    select(FundingKeyword.keyword).where(FundingKeyword.funding_opportunity_id == existing_opp.id)
                )
                existing_kws = {k.lower() for k in kw_res.scalars().all()}
                for kw in norm_opp.keywords:
                    clean_kw = kw.strip()
                    if clean_kw and clean_kw.lower() not in existing_kws:
                        existing_kws.add(clean_kw.lower())
                        db.add(FundingKeyword(funding_opportunity_id=existing_opp.id, keyword=clean_kw))

            existing_opp.updated_at = datetime.now(timezone.utc)
            await db.flush()
            refreshed = await FundingService.get_opportunity(existing_opp.id, db)
            return refreshed, "updated"

        # 3. Create new FundingOpportunity
        new_opp = FundingOpportunity(
            title=norm_opp.title.strip(),
            funding_agency=norm_opp.funding_agency.strip(),
            funding_program=norm_opp.funding_program.strip() if norm_opp.funding_program else None,
            description=norm_opp.description,
            funding_amount=norm_opp.funding_amount,
            currency=norm_opp.currency.upper() if norm_opp.currency else "USD",
            application_deadline=norm_opp.application_deadline,
            opportunity_type=norm_opp.opportunity_type or "Grant",
            eligibility_summary=norm_opp.eligibility_summary,
            eligible_institutions=norm_opp.eligible_institutions,
            geographic_restrictions=norm_opp.geographic_restrictions,
            status=norm_opp.status.lower() if norm_opp.status else "open",
            source=norm_opp.source.lower() if norm_opp.source else "manual",
            external_id=norm_opp.external_id,
            url=norm_opp.url,
            created_by_user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_opp)
        await db.flush()

        # Link Domains
        if norm_opp.domain_names:
            for d_name in norm_opp.domain_names:
                clean_d = d_name.strip()
                if not clean_d:
                    continue
                d_res = await db.execute(
                    select(ResearchDomain).where(func.lower(ResearchDomain.name) == clean_d.lower())
                )
                domain_obj = d_res.scalar_one_or_none()
                if not domain_obj:
                    domain_obj = ResearchDomain(name=clean_d, description=f"{clean_d} research domain")
                    db.add(domain_obj)
                    await db.flush()

                await db.execute(
                    funding_opportunity_domains.insert().values(
                        funding_opportunity_id=new_opp.id,
                        domain_id=domain_obj.id
                    )
                )

        # Link Keywords
        if norm_opp.keywords:
            seen_kw = set()
            for kw in norm_opp.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw.lower() not in seen_kw:
                    seen_kw.add(clean_kw.lower())
                    db.add(FundingKeyword(funding_opportunity_id=new_opp.id, keyword=clean_kw))

        await db.flush()
        persisted = await FundingService.get_opportunity(new_opp.id, db)
        return persisted, "inserted"

    @staticmethod
    async def ingest_opportunities(
        user_id: int,
        request: FundingIngestRequest,
        db: AsyncSession
    ) -> FundingIngestResponse:
        """
        Executes controlled ingestion from funding providers (Mock, Grants.gov, NSF, Horizon Europe),
        deduplicates, validates, persists records, and links domain taxonomies and keywords.
        """
        provider_name = request.provider or "mock"
        discovered: List[NormalizedFundingOpportunity] = []

        try:
            # Case 1: Ingest by external ID
            if request.external_id:
                opp = await funding_provider_service.fetch_by_id(
                    external_id=request.external_id.strip(),
                    preferred_provider=provider_name
                )
                if not opp:
                    raise EntityNotFoundException(
                        f"Funding opportunity with ID '{request.external_id}' could not be resolved from provider '{provider_name}'"
                    )
                discovered = [opp]

            # Case 2: Ingest by agency
            elif request.agency:
                prov = funding_provider_service.get_provider(provider_name)
                discovered = await prov.fetch_by_agency(agency_code=request.agency.strip(), limit=request.limit)

            # Case 3: Ingest by search query
            elif request.query:
                discovered = await funding_provider_service.search_opportunities(
                    query=request.query.strip(),
                    provider_name=provider_name,
                    limit=request.limit
                )

            else:
                raise CustomAPIException(
                    status_code=400,
                    code="INVALID_INGEST_PARAMS",
                    message="Must provide at least one of: 'external_id', 'query', or 'agency'"
                )

        except (ProviderTimeoutException, ProviderRateLimitException, ProviderNotFoundException) as pe:
            raise CustomAPIException(
                status_code=pe.status_code or 502,
                code="PROVIDER_ERROR",
                message=pe.message,
                details={"provider": pe.provider_name}
            )
        except ProviderException as pe:
            raise CustomAPIException(
                status_code=pe.status_code or 502,
                code="PROVIDER_ERROR",
                message=pe.message,
                details={"provider": pe.provider_name}
            )

        inserted_count = 0
        updated_count = 0
        duplicate_count = 0
        validation_failures = 0
        persisted_items: List[FundingOpportunity] = []

        for item in discovered:
            try:
                persisted, op_type = await FundingIngestService.persist_normalized_opportunity(
                    user_id=user_id,
                    norm_opp=item,
                    db=db
                )
                persisted_items.append(persisted)
                if op_type == "inserted":
                    inserted_count += 1
                elif op_type == "updated":
                    updated_count += 1
                    duplicate_count += 1
            except CustomAPIException as e:
                if e.code == "VALIDATION_ERROR":
                    validation_failures += 1
                else:
                    raise

        msg = (
            f"Discovered {len(discovered)} opportunity(ies): "
            f"{inserted_count} inserted, {updated_count} enriched/updated, "
            f"{validation_failures} validation failure(s)."
        )

        return FundingIngestResponse(
            discovered_count=len(discovered),
            inserted_count=inserted_count,
            updated_count=updated_count,
            duplicate_count=duplicate_count,
            validation_failures_count=validation_failures,
            opportunities=[FundingOpportunityRead.model_validate(p) for p in persisted_items],
            message=msg
        )
