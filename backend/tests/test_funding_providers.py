import pytest
from datetime import datetime

from app.services.providers.funding_base import NormalizedFundingOpportunity
from app.services.providers.funding_providers import (
    GrantsGovProvider,
    NSFFundingProvider,
    HorizonEuropeProvider,
    MockFundingProvider,
    FundingProviderService,
)
from app.services.providers.base import (
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
    ProviderException,
)


def test_grants_gov_payload_normalization():
    """Verifies parsing and normalization of Grants.gov search API records."""
    provider = GrantsGovProvider()

    raw_payload = {
        "id": "350123",
        "opportunityNumber": "HR0011-24-S-0001",
        "opportunityTitle": "Biological Technologies Office (BTO) Office-wide BAA",
        "agencyCode": "DARPA-BTO",
        "agencyName": "Defense Advanced Research Projects Agency",
        "awardCeiling": "3500000",
        "closeDate": "2025-09-30T23:59:59.000+0000",
        "oppStatuses": "posted",
        "fundingInstrumentType": "Procurement Contract",
        "synopsisDesc": "Revolutionary capabilities for biological computing and synthetic biology.",
        "eligibilityDesc": "Unrestricted"
    }

    norm = provider.normalize_opportunity(raw_payload)

    assert norm.title == "Biological Technologies Office (BTO) Office-wide BAA"
    assert norm.funding_agency == "Defense Advanced Research Projects Agency"
    assert norm.funding_amount == 3500000.0
    assert norm.currency == "USD"
    assert norm.status == "open"
    assert norm.opportunity_type == "Procurement Contract"
    assert norm.source == "grants_gov"
    assert norm.external_id == "HR0011-24-S-0001"
    assert "https://www.grants.gov/search-results-detail/HR0011-24-S-0001" in norm.url


def test_nsf_award_payload_normalization():
    """Verifies parsing and normalization of NSF public awards/solicitations records."""
    provider = NSFFundingProvider()

    raw_payload = {
        "id": "2312345",
        "title": "Collaborative Research: Scalable Fault-Tolerant Quantum Neutral Atom Architectures",
        "fundProgramName": "Quantum Information Science",
        "dirName": "Directorate for Mathematical and Physical Sciences",
        "fundsObligatedAmt": "800000",
        "abstractText": "This award supports the development of optical tweezer arrays for quantum simulation."
    }

    norm = provider.normalize_award(raw_payload)

    assert norm.title == raw_payload["title"]
    assert norm.funding_agency == "National Science Foundation"
    assert norm.funding_program == "Quantum Information Science"
    assert norm.funding_amount == 800000.0
    assert norm.source == "nsf"
    assert norm.external_id == "2312345"


def test_missing_fields_safe_handling():
    """Verifies that missing or null fields in provider payloads are handled safely without exceptions."""
    grants_gov = GrantsGovProvider()
    nsf = NSFFundingProvider()

    # Grants.gov empty dict
    norm_gg = grants_gov.normalize_opportunity({})
    assert norm_gg.title == "Untitled Grant Opportunity"
    assert norm_gg.funding_agency == "Federal Agency"
    assert norm_gg.funding_amount is None
    assert norm_gg.status == "open"

    # NSF empty dict
    norm_nsf = nsf.normalize_award({})
    assert norm_nsf.title == "NSF Award Opportunity"
    assert norm_nsf.funding_agency == "National Science Foundation"
    assert norm_nsf.funding_amount is None


@pytest.mark.asyncio
async def test_mock_funding_provider_operations():
    """Verifies deterministic search, ID lookup, and agency filtering in MockFundingProvider."""
    provider = MockFundingProvider()

    # 1. Fetch by external ID
    opp = await provider.fetch_by_id("NSF-24-548")
    assert opp is not None
    assert "ExpandQISE" in opp.title
    assert opp.funding_amount == 5000000.0
    assert "Quantum Technologies" in opp.domain_names

    # 2. Search opportunities
    results = await provider.search_opportunities("Nanoparticles", limit=5)
    assert len(results) >= 1
    assert "Targeted Nanoparticles" in results[0].title

    # 3. Fetch by agency
    agency_results = await provider.fetch_by_agency("Department of Energy", limit=5)
    assert len(agency_results) >= 1
    assert "ARPA-E" in agency_results[0].title


@pytest.mark.asyncio
async def test_mock_funding_provider_error_simulations():
    """Verifies timeout, rate limit, and not found error simulations."""
    timeout_provider = MockFundingProvider(simulate_timeout=True)
    with pytest.raises(ProviderTimeoutException):
        await timeout_provider.fetch_by_id("NSF-24-548")

    ratelimit_provider = MockFundingProvider(simulate_rate_limit=True)
    with pytest.raises(ProviderRateLimitException):
        await ratelimit_provider.search_opportunities("Quantum")

    notfound_provider = MockFundingProvider(simulate_not_found=True)
    with pytest.raises(ProviderNotFoundException):
        await notfound_provider.fetch_by_id("NONEXISTENT-ID")


@pytest.mark.asyncio
async def test_funding_provider_service_registry_and_dispatch():
    """Verifies FundingProviderService registry, provider lookup, and search dispatching."""
    service = FundingProviderService()

    # 1. List available providers
    available = service.list_available_providers()
    assert "grants_gov" in available
    assert "nsf" in available
    assert "horizon_europe" in available
    assert "mock" in available

    # 2. Lookup existing provider
    prov = service.get_provider("mock")
    assert prov.name == "mock"

    # 3. Lookup unsupported provider -> raises ProviderException
    with pytest.raises(ProviderException):
        service.get_provider("unsupported_funding_source")

    # 4. Fetch opportunity by ID via service
    opp = await service.fetch_by_id("R01-NS-132456", preferred_provider="mock")
    assert opp is not None
    assert opp.funding_agency == "National Institutes of Health"
