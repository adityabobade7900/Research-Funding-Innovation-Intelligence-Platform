import httpx
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.services.providers.base import (
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)
from app.services.providers.funding_base import BaseFundingProvider, NormalizedFundingOpportunity


SAMPLE_FUNDING_OPPORTUNITIES: List[Dict[str, Any]] = [
    {
        "title": "NSF ExpandQISE: Expanding Capacity in Quantum Information Science and Engineering",
        "funding_agency": "National Science Foundation",
        "funding_program": "Directorate for Mathematical and Physical Sciences",
        "description": "Aims to increase research capacity and broaden participation in Quantum Information Science and Engineering (QISE) across higher education institutions.",
        "funding_amount": 5000000.0,
        "currency": "USD",
        "application_deadline": datetime(2027, 10, 15, tzinfo=timezone.utc),
        "opportunity_type": "Grant",
        "eligibility_summary": "Higher education institutions not currently holding major QISE center grants.",
        "eligible_institutions": "Accredited US Universities & Colleges",
        "geographic_restrictions": "United States",
        "status": "open",
        "source": "mock",
        "external_id": "NSF-24-548",
        "url": "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505963",
        "keywords": ["Quantum Computing", "QISE", "Education Capacity", "Physics"],
        "domain_names": ["Quantum Technologies"]
    },
    {
        "title": "NIH Targeted Nanoparticles for Brain Delivery and Neurodegenerative Therapies",
        "funding_agency": "National Institutes of Health",
        "funding_program": "National Institute of Neurological Disorders and Stroke (NINDS)",
        "description": "Supports development and clinical translation of biomimetic lipid and polymer nanocarriers capable of crossing the blood-brain barrier for Alzheimer's and ALS treatment.",
        "funding_amount": 1800000.0,
        "currency": "USD",
        "application_deadline": datetime(2027, 11, 20, tzinfo=timezone.utc),
        "opportunity_type": "Grant",
        "eligibility_summary": "Universities, academic medical centers, and biotechnology small businesses.",
        "eligible_institutions": "Research Organizations & Universities",
        "geographic_restrictions": "United States & International Collaborations",
        "status": "open",
        "source": "mock",
        "external_id": "R01-NS-132456",
        "url": "https://grants.nih.gov/grants/guide/pa-files/PAR-24-101.html",
        "keywords": ["Nanomedicine", "Blood-Brain Barrier", "Lipid Nanoparticles", "Neurodegeneration"],
        "domain_names": ["Biotechnology & Genomic Sciences"]
    },
    {
        "title": "ARPA-E High-Efficiency Hydrogen Generation and Clean Energy Storage",
        "funding_agency": "Department of Energy",
        "funding_program": "Advanced Research Projects Agency - Energy (ARPA-E)",
        "description": "Focuses on high-risk, high-impact technologies for low-cost green hydrogen production via high-temperature electrolysis and advanced porous catalysts.",
        "funding_amount": 3200000.0,
        "currency": "USD",
        "application_deadline": datetime(2027, 12, 1, tzinfo=timezone.utc),
        "opportunity_type": "Contract",
        "eligibility_summary": "Industry-academic consortia, national laboratories, and commercial start-ups.",
        "eligible_institutions": "Consortia, Startups, National Labs",
        "geographic_restrictions": "United States",
        "status": "upcoming",
        "source": "mock",
        "external_id": "DE-FOA-0003123",
        "url": "https://arpa-e-foa.energy.gov/Default.aspx#FoaIdc34b8",
        "keywords": ["Hydrogen Energy", "Electrolysis", "Clean Energy", "Catalysis"],
        "domain_names": ["Clean Energy & Sustainability"]
    },
    {
        "title": "Horizon Europe EIC Pathfinder: Advanced Synthetic Biology and Bio-Manufacturing",
        "funding_agency": "European Commission",
        "funding_program": "European Innovation Council (EIC)",
        "description": "Supports early-stage scientific breakthroughs in synthetic genomics, cell-free biomanufacturing systems, and sustainable bio-based materials.",
        "funding_amount": 4000000.0,
        "currency": "EUR",
        "application_deadline": datetime(2027, 9, 10, tzinfo=timezone.utc),
        "opportunity_type": "Grant",
        "eligibility_summary": "Consortia of at least three legal entities from three different EU Member States or Associated Countries.",
        "eligible_institutions": "European Research Organizations & Enterprises",
        "geographic_restrictions": "EU Member States & Horizon Associated Countries",
        "status": "open",
        "source": "mock",
        "external_id": "HORIZON-EIC-2024-PATHFINDER-01",
        "url": "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/horizon-eic-2024-pathfinderopen-01-01",
        "keywords": ["Synthetic Biology", "Biomanufacturing", "Genomics", "EIC Pathfinder"],
        "domain_names": ["Biotechnology & Genomic Sciences"]
    }
]


class GrantsGovProvider(BaseFundingProvider):
    """
    Grants.gov Search2 API Client Abstraction.
    Endpoint: https://api.grants.gov/v1/api/opportunities/search
    """
    def __init__(self, base_url: str = "https://api.grants.gov/v1/api", timeout: float = 8.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "grants_gov"

    def normalize_opportunity(self, item: Dict[str, Any]) -> NormalizedFundingOpportunity:
        """Parses a Grants.gov opportunity object into NormalizedFundingOpportunity."""
        title = item.get("opportunityTitle") or item.get("title") or "Untitled Grant Opportunity"
        agency = item.get("agencyName") or item.get("agencyCode") or "Federal Agency"
        opp_number = item.get("opportunityNumber") or item.get("id")
        desc = item.get("description") or item.get("synopsisDesc")

        amount = None
        award_ceiling = item.get("awardCeiling")
        if award_ceiling is not None:
            try:
                amount = float(award_ceiling)
            except (ValueError, TypeError):
                pass

        deadline = None
        close_date_str = item.get("closeDate")
        if close_date_str:
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    deadline = datetime.strptime(close_date_str[:10], fmt[:8]).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue

        status_str = "open"
        raw_status = str(item.get("oppStatuses") or item.get("status") or "").lower()
        if "closed" in raw_status or "archived" in raw_status:
            status_str = "closed"
        elif "forecasted" in raw_status or "upcoming" in raw_status:
            status_str = "upcoming"

        url = f"https://www.grants.gov/search-results-detail/{opp_number}" if opp_number else None

        return NormalizedFundingOpportunity(
            title=title,
            funding_agency=agency,
            funding_program=item.get("fundingInstrumentType"),
            description=desc,
            funding_amount=amount,
            currency="USD",
            application_deadline=deadline,
            opportunity_type=item.get("fundingInstrumentType") or "Grant",
            eligibility_summary=item.get("eligibilityDesc"),
            status=status_str,
            source=self.name,
            external_id=str(opp_number) if opp_number else None,
            url=url,
            raw_payload=item
        )

    async def fetch_by_id(self, external_id: str) -> Optional[NormalizedFundingOpportunity]:
        return NormalizedFundingOpportunity(
            title=f"Grants.gov Opportunity {external_id}",
            funding_agency="US Federal Agency",
            source=self.name,
            external_id=external_id,
            url=f"https://www.grants.gov/search-results-detail/{external_id}"
        )

    async def search_opportunities(self, query: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []

    async def fetch_by_agency(self, agency_code: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []


class NSFFundingProvider(BaseFundingProvider):
    """
    National Science Foundation (NSF) Public API Provider Abstraction.
    Endpoint: https://api.nsf.gov/services/v1/awards.json
    """
    def __init__(self, base_url: str = "https://api.nsf.gov/services/v1", timeout: float = 8.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "nsf"

    def normalize_award(self, item: Dict[str, Any]) -> NormalizedFundingOpportunity:
        title = item.get("title") or "NSF Award Opportunity"
        agency = "National Science Foundation"
        award_id = item.get("id")

        amount = None
        funds = item.get("fundsObligatedAmt") or item.get("estimatedTotalAmt")
        if funds:
            try:
                amount = float(funds)
            except (ValueError, TypeError):
                pass

        return NormalizedFundingOpportunity(
            title=title,
            funding_agency=agency,
            funding_program=item.get("fundProgramName") or item.get("dirName"),
            description=item.get("abstractText"),
            funding_amount=amount,
            currency="USD",
            opportunity_type="Grant",
            status="open",
            source=self.name,
            external_id=str(award_id) if award_id else None,
            url=f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={award_id}" if award_id else None,
            domain_names=[item.get("dirName")] if item.get("dirName") else [],
            raw_payload=item
        )

    async def fetch_by_id(self, external_id: str) -> Optional[NormalizedFundingOpportunity]:
        return NormalizedFundingOpportunity(
            title=f"NSF Program {external_id}",
            funding_agency="National Science Foundation",
            source=self.name,
            external_id=external_id,
            url=f"https://www.nsf.gov/awardsearch/showAward?AWD_ID={external_id}"
        )

    async def search_opportunities(self, query: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []

    async def fetch_by_agency(self, agency_code: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []


class HorizonEuropeProvider(BaseFundingProvider):
    """
    European Commission Horizon Europe & CORDIS Provider Abstraction.
    """
    @property
    def name(self) -> str:
        return "horizon_europe"

    async def fetch_by_id(self, external_id: str) -> Optional[NormalizedFundingOpportunity]:
        return NormalizedFundingOpportunity(
            title=f"Horizon Europe Topic {external_id}",
            funding_agency="European Commission",
            currency="EUR",
            source=self.name,
            external_id=external_id,
            url=f"https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-details/{external_id}"
        )

    async def search_opportunities(self, query: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []

    async def fetch_by_agency(self, agency_code: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        return []


class MockFundingProvider(BaseFundingProvider):
    """
    Deterministic Mock Funding Provider with pre-seeded federal and international RFPs,
    supporting keyword search, agency filtering, and configurable error simulations.
    """
    def __init__(
        self,
        simulate_timeout: bool = False,
        simulate_rate_limit: bool = False,
        simulate_not_found: bool = False
    ):
        self.simulate_timeout = simulate_timeout
        self.simulate_rate_limit = simulate_rate_limit
        self.simulate_not_found = simulate_not_found
        self._opportunities: List[NormalizedFundingOpportunity] = [
            NormalizedFundingOpportunity(
                title=o["title"],
                funding_agency=o["funding_agency"],
                funding_program=o["funding_program"],
                description=o["description"],
                funding_amount=o["funding_amount"],
                currency=o["currency"],
                application_deadline=o["application_deadline"],
                opportunity_type=o["opportunity_type"],
                eligibility_summary=o["eligibility_summary"],
                eligible_institutions=o["eligible_institutions"],
                geographic_restrictions=o["geographic_restrictions"],
                status=o["status"],
                source=o["source"],
                external_id=o["external_id"],
                url=o["url"],
                keywords=o["keywords"],
                domain_names=o["domain_names"]
            )
            for o in SAMPLE_FUNDING_OPPORTUNITIES
        ]

    @property
    def name(self) -> str:
        return "mock"

    def _check_simulation(self, identifier: str = "mock-req"):
        if self.simulate_timeout:
            raise ProviderTimeoutException(provider_name=self.name, timeout_seconds=8.0)
        if self.simulate_rate_limit:
            raise ProviderRateLimitException(provider_name=self.name, retry_after=30)
        if self.simulate_not_found:
            raise ProviderNotFoundException(provider_name=self.name, identifier=identifier)

    async def fetch_by_id(self, external_id: str) -> Optional[NormalizedFundingOpportunity]:
        self._check_simulation(external_id)
        for opp in self._opportunities:
            if opp.external_id and opp.external_id.lower() == external_id.lower():
                return opp
        return None

    async def search_opportunities(self, query: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        self._check_simulation(query)
        q_lower = query.lower()
        results = [
            o for o in self._opportunities
            if q_lower in o.title.lower()
            or (o.description and q_lower in o.description.lower())
            or q_lower in o.funding_agency.lower()
            or (o.funding_program and q_lower in o.funding_program.lower())
            or any(q_lower in k.lower() for k in o.keywords)
            or any(q_lower in d.lower() for d in o.domain_names)
        ]
        return results[:limit]

    async def fetch_by_agency(self, agency_code: str, limit: int = 20) -> List[NormalizedFundingOpportunity]:
        self._check_simulation(agency_code)
        a_lower = agency_code.lower()
        results = [o for o in self._opportunities if a_lower in o.funding_agency.lower()]
        return results[:limit]


class FundingProviderService:
    def __init__(self):
        self._providers: Dict[str, BaseFundingProvider] = {
            "grants_gov": GrantsGovProvider(),
            "nsf": NSFFundingProvider(),
            "horizon_europe": HorizonEuropeProvider(),
            "mock": MockFundingProvider(),
        }

    def register_provider(self, provider: BaseFundingProvider) -> None:
        self._providers[provider.name.lower()] = provider

    def get_provider(self, name: str) -> BaseFundingProvider:
        clean_name = name.strip().lower()
        if clean_name not in self._providers:
            raise ProviderException(
                message=f"Funding provider '{name}' is not supported",
                provider_name=name
            )
        return self._providers[clean_name]

    def list_available_providers(self) -> List[str]:
        return list(self._providers.keys())

    async def fetch_by_id(
        self,
        external_id: str,
        preferred_provider: Optional[str] = None
    ) -> Optional[NormalizedFundingOpportunity]:
        if preferred_provider:
            provider = self.get_provider(preferred_provider)
            return await provider.fetch_by_id(external_id)

        for p_name in ["mock", "grants_gov", "nsf", "horizon_europe"]:
            if p_name in self._providers:
                try:
                    provider = self._providers[p_name]
                    opp = await provider.fetch_by_id(external_id)
                    if opp:
                        return opp
                except Exception:
                    continue
        return None

    async def search_opportunities(
        self,
        query: str,
        provider_name: str = "mock",
        limit: int = 20
    ) -> List[NormalizedFundingOpportunity]:
        provider = self.get_provider(provider_name)
        return await provider.search_opportunities(query=query, limit=limit)


funding_provider_service = FundingProviderService()
