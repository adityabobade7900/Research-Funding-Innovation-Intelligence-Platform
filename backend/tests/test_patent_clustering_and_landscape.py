import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

from tests.conftest import TestingSessionLocal
from app.models.patent import Patent, profile_patents
from app.models.user import User, UserRole
from app.models.profile import Profile
from app.models.research_domain import ResearchDomain
from app.core.security import get_password_hash
from app.services.patent_clustering_service import PatentClusteringService
from app.services.patent_landscape_service import PatentLandscapeService


@pytest_asyncio.fixture
async def rich_clustering_corpus():
    """
    Seeds a rich deterministic patent corpus across Quantum Computing, Biotechnology, and Clean Energy.
    """
    patents = [
        # Quantum Computing cluster
        {
            "patent_number": "US10111222B2",
            "title": "Superconducting Qubit Coupler for Fault-Tolerant Quantum Processor",
            "abstract": "Methods and apparatus for tunable coupling between superconducting transmon qubits using flux bias loops.",
            "assignee": "IBM Corporation",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 35,
            "filing_date": datetime(2021, 3, 15, tzinfo=timezone.utc),
            "publication_date": datetime(2022, 9, 20, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US10222333B2",
            "title": "Cryogenic Control Circuitry for Scalable Superconducting Qubits",
            "abstract": "CMOS integrated circuit operating at sub-Kelvin temperatures to control multi-qubit pulse sequences.",
            "assignee": "IBM Corporation",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 22,
            "filing_date": datetime(2022, 5, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 3, 14, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US10333444B2",
            "title": "Neutral Atom Qubit Arrays with Dynamic Optical Tweezers",
            "abstract": "Reconfigurable neutral atom qubit register using acousto-optic deflectors for high-fidelity quantum gates.",
            "assignee": "Google LLC",
            "technology_domain": "Quantum Computing",
            "patent_classification": "G06N 10/00",
            "citation_count": 18,
            "filing_date": datetime(2023, 1, 10, tzinfo=timezone.utc),
            "publication_date": datetime(2024, 4, 5, tzinfo=timezone.utc),
        },
        # Biotechnology cluster
        {
            "patent_number": "US10444555B1",
            "title": "Engineered Cas12 Nucleases for High-Fidelity Gene Editing",
            "abstract": "Engineered CRISPR Cas nucleases exhibiting reduced off-target cleavage in human therapeutic gene editing.",
            "assignee": "Broad Institute",
            "technology_domain": "Biotechnology",
            "patent_classification": "C12N 15/113",
            "citation_count": 48,
            "filing_date": datetime(2020, 8, 12, tzinfo=timezone.utc),
            "publication_date": datetime(2021, 6, 25, tzinfo=timezone.utc),
        },
        {
            "patent_number": "US10555666B1",
            "title": "Ionizable Lipid Nanoparticle Formulations for Therapeutic mRNA Delivery",
            "abstract": "Lipid nanoparticle compositions comprising novel ionizable lipids for organ-selective delivery of mRNA vaccines.",
            "assignee": "ModernaTX, Inc.",
            "technology_domain": "Biotechnology",
            "patent_classification": "A61K 9/51",
            "citation_count": 62,
            "filing_date": datetime(2021, 2, 20, tzinfo=timezone.utc),
            "publication_date": datetime(2022, 11, 15, tzinfo=timezone.utc),
        },
        {
            "patent_number": "EP3666777A1",
            "title": "Targeted Gene Delivery Vectors Utilizing Synthetic Lipid Nanoparticles",
            "abstract": "Formulations for delivering mRNA and nucleic acid therapeutic agents to hepatic tissue.",
            "assignee": "BioNTech SE",
            "technology_domain": "Biotechnology",
            "patent_classification": "A61K 48/00",
            "citation_count": 30,
            "filing_date": datetime(2022, 10, 5, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 8, 18, tzinfo=timezone.utc),
        },
        # Clean Energy cluster
        {
            "patent_number": "EP3777888B1",
            "title": "Solid-State Electrolyte Compositions for High Energy Density Lithium Batteries",
            "abstract": "Sulfide-based solid electrolytes with high ionic conductivity and electrochemical stability exceeding 5V.",
            "assignee": "QuantumScape Battery Corp",
            "technology_domain": "Clean Energy",
            "patent_classification": "H01M 10/0562",
            "citation_count": 25,
            "filing_date": datetime(2021, 6, 18, tzinfo=timezone.utc),
            "publication_date": datetime(2022, 12, 10, tzinfo=timezone.utc),
        },
        {
            "patent_number": "WO2023112233A1",
            "title": "Direct Air Capture Sorbent Regeneration for Carbon Removal Systems",
            "abstract": "Energy-efficient solid sorbent direct air contactors operating under vacuum desorption conditions.",
            "assignee": "Climeworks AG",
            "technology_domain": "Clean Energy",
            "patent_classification": "B01D 53/04",
            "citation_count": 12,
            "filing_date": datetime(2023, 4, 12, tzinfo=timezone.utc),
            "publication_date": datetime(2023, 10, 20, tzinfo=timezone.utc),
        },
    ]

    async with TestingSessionLocal() as session:
        created = []
        for p_data in patents:
            pat = Patent(
                patent_number=p_data["patent_number"],
                title=p_data["title"],
                abstract=p_data["abstract"],
                assignee=p_data["assignee"],
                technology_domain=p_data["technology_domain"],
                patent_classification=p_data["patent_classification"],
                citation_count=p_data["citation_count"],
                filing_date=p_data["filing_date"],
                publication_date=p_data["publication_date"],
                source="manual",
            )
            session.add(pat)
            created.append(pat)
        await session.commit()
        for p in created:
            await session.refresh(p)
        return created


@pytest.mark.asyncio
async def test_real_machine_learning_clustering(rich_clustering_corpus):
    """
    Verifies that the unsupervised clustering engine performs REAL TF-IDF + K-Means clustering,
    computes cluster centroids, dominant terms, member distances, and explainable summaries.
    """
    async with TestingSessionLocal() as session:
        res = await PatentClusteringService.cluster_patents(db=session, k=3)

        assert res.total_patents == 8
        assert res.total_clusters == 3
        assert res.algorithm == "TF-IDF Vectorization + K-Means Clustering"
        assert res.k_requested == 3
        assert len(res.clusters) == 3

        # Verify cluster centroids and dominant terms
        all_dominant_terms = []
        for c in res.clusters:
            assert c.patent_count > 0
            assert c.share_percentage > 0.0
            assert len(c.dominant_terms) >= 1
            all_dominant_terms.extend(c.dominant_terms)

            # Check representative patents
            assert len(c.representative_patents) == c.patent_count
            for member in c.representative_patents:
                assert member.distance_to_centroid is not None
                assert member.distance_to_centroid >= 0.0
                assert "distance" in member.explanation

            # Representative patents must be sorted by distance ascending (nearest to centroid first)
            dists = [m.distance_to_centroid for m in c.representative_patents if m.distance_to_centroid is not None]
            assert dists == sorted(dists)

        # Technical terms from our domains should be represented in centroids
        assert any(t in str(all_dominant_terms).lower() for t in ["qubit", "lipid", "mrna", "electrolyte", "cas12", "superconducting", "battery"])


@pytest.mark.asyncio
async def test_clustering_edge_cases_handling():
    """
    Verifies that small datasets (0 patents, 1 patent, 2 patents) are handled gracefully without runtime exceptions.
    """
    async with TestingSessionLocal() as session:
        # Edge Case 1: 0 patents
        res_empty = await PatentClusteringService.cluster_patents(db=session, domain="NonExistentDomain")
        assert res_empty.total_patents == 0
        assert res_empty.total_clusters == 0
        assert res_empty.clusters == []

        # Edge Case 2: 1 patent (singleton partition)
        single_pat = Patent(
            patent_number="US99990001B2",
            title="Single Qubit Optical Sensor Architecture",
            abstract="Quantum sensor utilizing single photon emitters.",
            technology_domain="Quantum Technologies",
            patent_classification="G06N10/00",
            citation_count=10,
            source="manual"
        )
        session.add(single_pat)
        await session.commit()
        await session.refresh(single_pat)

        res_single = await PatentClusteringService.cluster_patents(db=session, domain="Quantum Technologies")
        assert res_single.total_patents == 1
        assert res_single.total_clusters == 1
        assert res_single.clusters[0].patent_count == 1
        assert res_single.clusters[0].representative_patents[0].distance_to_centroid == 0.0
        assert "singleton" in res_single.clusters[0].representative_patents[0].explanation.lower()

        # Edge Case 3: Requested k larger than total patents
        res_bounded = await PatentClusteringService.cluster_patents(db=session, domain="Quantum Technologies", k=10)
        assert res_bounded.total_clusters <= res_bounded.total_patents


@pytest.mark.asyncio
async def test_patent_clustering_api_endpoint(client: AsyncClient, rich_clustering_corpus):
    """
    Validates GET /api/v1/patent-intelligence/clusters endpoint.
    """
    # 1. Global clustering
    resp = await client.get("/api/v1/patent-intelligence/clusters?k=3")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_patents"] == 8
    assert data["total_clusters"] == 3
    assert "TF-IDF" in data["algorithm"]

    # 2. Filtered clustering
    resp_filtered = await client.get("/api/v1/patent-intelligence/clusters?domain=Quantum")
    assert resp_filtered.status_code == 200
    filtered_data = resp_filtered.json()["data"]
    assert filtered_data["total_patents"] == 3
    assert filtered_data["clusters"][0]["technology_domain"] == "Quantum Computing"


@pytest.mark.asyncio
async def test_assignee_concentration_hhi_and_weighting(client: AsyncClient, rich_clustering_corpus):
    """
    Verifies that Assignee HHI is computed and Composite Competitive Index contains weighting metadata.
    """
    # 1. Assignees HHI
    ass_resp = await client.get("/api/v1/patent-intelligence/assignees")
    assert ass_resp.status_code == 200
    ass_data = ass_resp.json()["data"]
    assert "assignee_concentration_hhi" in ass_data
    assert ass_data["assignee_concentration_hhi"] > 0
    assert ass_data["concentration_level"] in ["DIVERSIFIED", "MODERATELY_CONCENTRATED", "HIGHLY_CONCENTRATED"]

    # 2. Competitive Landscape with weighting schema
    comp_resp = await client.get("/api/v1/patent-intelligence/competitive-landscape")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()["data"]
    assert comp_data["assignee_concentration_hhi"] == ass_data["assignee_concentration_hhi"]
    assert comp_data["weighting_schema"]["volume"] == 0.40
    assert comp_data["weighting_schema"]["velocity"] == 0.30
    assert comp_data["weighting_schema"]["citations"] == 0.20
    assert comp_data["weighting_schema"]["domain_breadth"] == 0.10


@pytest.mark.asyncio
async def test_innovation_mapping_api_endpoint(client: AsyncClient, rich_clustering_corpus):
    """
    Validates GET /api/v1/patent-intelligence/innovation-map endpoint.
    """
    resp = await client.get("/api/v1/patent-intelligence/innovation-map")
    assert resp.status_code == 200
    res_data = resp.json()["data"]

    assert res_data["total_patents"] == 8
    assert len(res_data["domains"]) >= 3
    assert len(res_data["assignees"]) >= 5
    assert len(res_data["classifications"]) >= 4

    # Check matrix cells
    assert len(res_data["matrix"]) >= 4
    first_cell = res_data["matrix"][0]
    assert first_cell["domain"] != ""
    assert first_cell["assignee"] != ""
    assert first_cell["patent_count"] >= 1
    assert len(first_cell["patent_numbers"]) >= 1

    # Check hotspots
    assert len(res_data["hotspots"]) >= 1
    hotspot = res_data["hotspots"][0]
    assert hotspot["activity_type"] in ["EXPANDING_CORE", "HIGH_GROWTH", "EMERGING"]

    # Check whitespaces
    assert len(res_data["whitespaces"]) >= 1
    whitespace = res_data["whitespaces"][0]
    assert whitespace["opportunity_level"] in ["HIGH", "MEDIUM", "MODERATE"]


@pytest.mark.asyncio
async def test_patent_bookmarking_lifecycle(client: AsyncClient, test_user: dict):
    """
    Verifies full bookmarking lifecycle: bookmark, inspect state, list in /my, and unbookmark.
    """
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create standalone patent
    async with TestingSessionLocal() as session:
        standalone = Patent(
            patent_number="US99881122B2",
            title="Cryogenic CMOS Multiplexer for Scalable Readout",
            assignee="ColdLab Inc",
            technology_domain="Quantum Computing",
            citation_count=5,
            source="manual"
        )
        session.add(standalone)
        await session.commit()
        await session.refresh(standalone)
        pat_id = standalone.id

    # 3. Get patent before bookmark -> is_bookmarked is False
    get_before = await client.get(f"/api/v1/patents/{pat_id}", headers=headers)
    assert get_before.status_code == 200
    assert get_before.json()["data"]["is_bookmarked"] is False

    # 4. Bookmark patent
    bm_resp = await client.post(f"/api/v1/patents/{pat_id}/bookmark", headers=headers)
    assert bm_resp.status_code == 200
    assert bm_resp.json()["data"]["bookmarked"] is True

    # 5. Get patent after bookmark -> is_bookmarked is True
    get_after = await client.get(f"/api/v1/patents/{pat_id}", headers=headers)
    assert get_after.status_code == 200
    assert get_after.json()["data"]["is_bookmarked"] is True

    # 6. Appears in /my
    my_resp = await client.get("/api/v1/patents/my", headers=headers)
    assert my_resp.status_code == 200
    assert pat_id in [p["id"] for p in my_resp.json()["data"]["items"]]

    # 7. Remove bookmark
    del_resp = await client.delete(f"/api/v1/patents/{pat_id}/bookmark", headers=headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["bookmarked"] is False

    # 8. Get patent after unbookmark -> is_bookmarked is False
    get_unbookmarked = await client.get(f"/api/v1/patents/{pat_id}", headers=headers)
    assert get_unbookmarked.json()["data"]["is_bookmarked"] is False


@pytest.mark.asyncio
async def test_profile_based_patent_recommendations(client: AsyncClient, rich_clustering_corpus):
    """
    Module 3 Integration:
    Verifies that researcher profile domains and keywords yield explainable patent recommendations,
    excluding patents already linked to the researcher's profile.
    """
    async with TestingSessionLocal() as session:
        # Create user with profile interested in Quantum Computing & Qubits
        user = User(
            email="quantum_researcher@mit.edu",
            hashed_password=get_password_hash("password123"),
            full_name="Dr. Alice Quantum",
            role=UserRole.RESEARCHER,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        from app.models.research_domain import ResearchDomain, ResearchInterest, ProfileKeyword

        domain = ResearchDomain(name="Quantum Computing", description="Quantum Computing Domain")
        session.add(domain)
        await session.commit()
        await session.refresh(domain)

        profile = Profile(
            user_id=user.id,
            institution="MIT Center for Ultracold Atoms",
            domains=[domain]
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

        session.add(ResearchInterest(profile_id=profile.id, title="qubit"))
        session.add(ResearchInterest(profile_id=profile.id, title="cryogenic"))
        session.add(ProfileKeyword(profile_id=profile.id, keyword="superconducting"))
        await session.commit()
        await session.refresh(profile)

        # Link ONE Quantum patent (US10111222B2) to profile so it must be EXCLUDED from recommendations
        linked_pat = next(p for p in rich_clustering_corpus if p.patent_number == "US10111222B2")
        await session.execute(
            profile_patents.insert().values(
                profile_id=profile.id,
                patent_id=linked_pat.id,
                created_at=datetime.now(timezone.utc)
            )
        )
        await session.commit()

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "quantum_researcher@mit.edu", "password": "password123"}
    )
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch recommendations
    rec_resp = await client.get("/api/v1/patent-intelligence/recommendations?limit=5", headers=headers)
    assert rec_resp.status_code == 200
    res_data = rec_resp.json()["data"]

    assert res_data["total_recommendations"] > 0
    recs = res_data["recommendations"]

    # 1. Already linked patent US10111222B2 MUST NOT be recommended
    rec_patent_numbers = [r["patent_number"] for r in recs]
    assert "US10111222B2" not in rec_patent_numbers

    # 2. Top recommendation should be an unlinked Quantum Computing patent (US10222333B2 or US10333444B2)
    top_rec = recs[0]
    assert top_rec["technology_domain"] == "Quantum Computing"
    assert top_rec["match_score"] >= 50.0
    assert "Quantum Computing" in top_rec["matched_domains"]
    assert len(top_rec["rationale"]) > 0
