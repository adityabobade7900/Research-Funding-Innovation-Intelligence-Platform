# 12_EXTERNAL_DATA_SOURCES.md — External Data Sources & Provider Adapters

## 1. Provider Adapter Architecture

External data harvesters are organized modularly in `backend/app/services/providers/`:
- **Base Interfaces:** `BaseResearchProvider`, `BaseFundingProvider`, `BasePatentProvider`.
- **Normalization Contracts:** Standardized dataclasses (`NormalizedPublication`, `NormalizedFundingOpportunity`, `NormalizedPatent`).
- **Resilience:** Configurable timeouts (`PROVIDER_TIMEOUT_SECONDS`), automatic retries, and comprehensive offline mock fallbacks.

---

## 2. Implemented External Data Harvester Adapters

### 2.1. OpenAlex API
- **Source Name:** OpenAlex
- **Domain Purpose:** Academic scientific publications, citation counts, and authors.
- **Provider Class:** `OpenAlexProvider` in `backend/app/services/providers/openalex.py`
- **Base Endpoint:** `https://api.openalex.org/works`
- **Authentication:** None required; polite pool supported via `mailto` query parameter.
- **Environment Variable:** `OPENALEX_EMAIL` (Optional)
- **Key Fields Retrieved:** Title, inverted index abstract, publication year, publication date, DOI, primary location venue, citation count, authorships, concepts/fields of study.
- **Special Logic:** Reconstructs full-text abstract from the OpenAlex inverted index dictionary structure (`_reconstruct_abstract`).
- **Rate Limits:** Polite pool allows up to 10 requests/sec.
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_providers.py`).

### 2.2. Crossref REST API
- **Source Name:** Crossref
- **Domain Purpose:** DOI bibliographic metadata resolution and verification.
- **Provider Class:** `CrossrefProvider` in `backend/app/services/providers/crossref.py`
- **Base Endpoint:** `https://api.crossref.org/works`
- **Authentication:** None required; polite headers supported via `User-Agent` / `mailto`.
- **Environment Variable:** `CROSSREF_MAILTO` (Optional)
- **Key Fields Retrieved:** Title, container-title (venue), published-print / published-online date, author array (given, family), DOI, reference count, URL.
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_providers.py`).

### 2.3. Semantic Scholar Graph API
- **Source Name:** Semantic Scholar (Allen Institute for AI)
- **Domain Purpose:** Research paper citation metrics, abstracts, and fields of study.
- **Provider Class:** `SemanticScholarProvider` in `backend/app/services/providers/semantic_scholar.py`
- **Base Endpoint:** `https://api.semanticscholar.org/graph/v1/paper`
- **Authentication:** Optional API key via `x-api-key` header.
- **Environment Variable:** `SEMANTIC_SCHOLAR_API_KEY` (Optional)
- **Fields Retrieved:** `title,abstract,authors,year,publicationDate,venue,externalIds,citationCount,fieldsOfStudy,s2FieldsOfStudy,url`.
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_providers.py`).

### 2.4. Grants.gov Public Search
- **Source Name:** Grants.gov
- **Domain Purpose:** US Federal grant solicitations and RFP announcements.
- **Provider Class:** `GrantsGovProvider` in `backend/app/services/providers/funding_providers.py`
- **Base Endpoint:** `https://api.grants.gov/v1/api/opportunities` (simulated/modeled client)
- **Authentication:** None required for public search.
- **Environment Variable:** None currently required.
- **Fields Retrieved:** Opportunity number, title, agency code/name, funding instrument type, estimated funding amount, close date (deadline), eligibility description, CFDA numbers.
- **Fallback Behavior:** Seamless fallback to curated US federal grant fixtures.
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_funding_providers.py`).

### 2.5. National Science Foundation (NSF) Awards API
- **Source Name:** NSF Awards Search API
- **Domain Purpose:** NSF scientific research grants, award amounts, and directorates.
- **Provider Class:** `NSFFundingProvider` in `backend/app/services/providers/funding_providers.py`
- **Base Endpoint:** `https://api.nsf.gov/services/v1/awards.json`
- **Authentication:** None required (Public US Government API).
- **Environment Variable:** None required.
- **Fields Retrieved:** Award ID, title, abstractText, fundsObligatedAmt, dirName (directorate), fundProgramName, startDate, expDate.
- **Fallback Behavior:** Built-in offline fallback fixtures covering Quantum, AI, and Nanotech awards.
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_funding_providers.py`).

### 2.6. Google Patents / Canonical Patent Identifier Client
- **Source Name:** Google Patents
- **Domain Purpose:** Resolves canonical patent URLs, numbers, and structured metadata.
- **Provider Class:** `GooglePatentsProvider` in `backend/app/services/providers/patent_providers.py`
- **Mechanism:** Formulates canonical `patents.google.com/patent/{PATENT_NUMBER}/en` links and normalizes patent identifiers (e.g., `US11234567B2`).
- **Implementation Status:** 🟢 **IMPLEMENTED & TESTED** (Unit tested in `backend/tests/test_providers.py`).

---

## 3. Proposed But Not Yet Implemented External Sources

The following external sources were listed in project specification documents but have **NOT** been integrated into active source code:

1. **USPTO Public Open Data Portal (Bulk / API):**  
   Direct USPTO API v2 connection is planned for live US patent status tracking. Currently simulated via `GooglePatentsProvider` and mock datasets.
2. **The Lens (lens.org):**  
   Specified for global patent family and citation linking. Requires paid API subscription.
3. **Horizon Europe / CORDIS (Live REST Stream):**  
   Stub class `HorizonEuropeProvider` exists in code, but live HTTP endpoint parsing is not completed.
4. **IEEE Xplore & Scopus:**  
   Proprietary publisher APIs requiring paid institutional API keys.
