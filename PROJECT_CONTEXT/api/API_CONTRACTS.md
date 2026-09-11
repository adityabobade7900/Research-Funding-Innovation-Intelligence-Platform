# api/API_CONTRACTS.md — Data Contracts & Payload Schemas

> **PAYLOAD STANDARD:** All request and response bodies use strictly typed Pydantic v2 schemas (`backend/app/schemas/`) and corresponding TypeScript interfaces (`frontend/src/lib/`).

---

## 1. Authentication & Token Contracts

### 1.1. Registration Request & Response
- **Endpoint:** `POST /api/v1/auth/register`
- **Request Body (`UserRegister`):**
  ```json
  {
    "email": "user@university.edu",
    "password": "SecurePassword123!",
    "full_name": "Dr. Jane Doe",
    "role": "researcher",
    "phone": "+1-555-0199"
  }
  ```
  *Allowed roles:* `researcher`, `startup_founder`, `innovation_manager`. (`administrator` is rejected with HTTP 403).
- **Response Body (`UserRead`, HTTP 201):**
  ```json
  {
    "id": 10,
    "email": "user@university.edu",
    "full_name": "Dr. Jane Doe",
    "role": "researcher",
    "phone": "+1-555-0199",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2026-09-11T03:00:00Z"
  }
  ```

### 1.2. Login Response & Token Refresh
- **Endpoint:** `POST /api/v1/auth/login` and `POST /api/v1/auth/refresh`
- **Response Body (`TokenResponse`, HTTP 200):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
    "refresh_token": "9aBcDeF_cryptographic_48_byte_token_string...",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

---

## 2. Research Profile Contracts

- **Endpoint:** `GET /api/v1/profile/me` and `PUT /api/v1/profile/me`
- **Response Model (`ExtendedProfileRead`):**
  ```json
  {
    "id": 1,
    "user_id": 1,
    "full_name": "Dr. Jane Doe",
    "email": "user@university.edu",
    "role": "researcher",
    "institution": "Stanford University",
    "department": "Applied Physics",
    "designation": "Associate Professor",
    "country": "United States",
    "bio": "Investigating neutral atom quantum architectures.",
    "orcid_id": "0000-0002-1825-0097",
    "website": "https://lab.stanford.edu/doe",
    "domains": [
      {"id": 1, "name": "Quantum Technologies"}
    ],
    "interests": [
      {"id": 1, "title": "Optical Tweezer Arrays", "importance_level": 5}
    ],
    "keywords": ["Quantum Computing", "Neutral Atoms", "Rydberg States"],
    "technology_areas": [
      {"id": 1, "name": "Quantum Information Systems"}
    ],
    "academic_history": [
      {"degree": "Ph.D.", "field_of_study": "Physics", "institution": "MIT", "end_year": 2018}
    ],
    "research_history": [
      {"project_title": "Scalable Qubit Trapping", "role": "Principal Investigator", "organization": "NSF"}
    ]
  }
  ```

---

## 3. Scientific Publication Contracts

- **Endpoint:** `GET /api/v1/publications/{id}`
- **Response Model (`PublicationRead`):**
  ```json
  {
    "id": 1,
    "title": "Neutral Atom Quantum Processor Architecture with Dynamic Optical Tweezer Arrays",
    "authors": "Dr. Vance Adams, Dr. Mikhail Lukin",
    "abstract": "Methods and systems for arranging and addressing neutral atoms...",
    "publication_date": "2023-01-17",
    "venue": "Nature Physics",
    "doi": "10.1038/s41567-023-01999-x",
    "citation_count": 28,
    "primary_domain": "Quantum Technologies",
    "source": "semanticscholar",
    "external_id": "S2-987654321",
    "url": "https://doi.org/10.1038/s41567-023-01999-x"
  }
  ```

---

## 4. Funding Opportunity Contracts

- **Endpoint:** `GET /api/v1/funding/{id}`
- **Response Model (`FundingOpportunityRead`):**
  ```json
  {
    "id": 1,
    "title": "NSF ExpandQISE: Expanding Capacity in Quantum Information Science",
    "funding_agency": "National Science Foundation",
    "funding_program": "Mathematical and Physical Sciences",
    "description": "Aims to increase research capacity in quantum information science...",
    "funding_amount": 5000000.00,
    "currency": "USD",
    "application_deadline": "2027-10-15T00:00:00Z",
    "opportunity_type": "Grant",
    "eligibility_summary": "Higher education institutions not holding center grants.",
    "eligible_institutions": "Accredited US Universities",
    "geographic_restrictions": "United States",
    "status": "open",
    "source": "nsf",
    "external_id": "NSF-24-548",
    "url": "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505963"
  }
  ```

---

## 5. Innovation Scoring & TRL Contracts

- **Endpoint:** `GET /api/v1/innovation-scoring/score?domain=Quantum+Technologies`
- **Response Model (`InnovationScoreResponse`):**
  ```json
  {
    "domain": "Quantum Technologies",
    "composite_innovation_score": 84.50,
    "rating_classification": "HIGH_INNOVATION_POTENTIAL",
    "pillars": [
      {
        "pillar_name": "Research Novelty",
        "weight_percentage": 30.0,
        "score": 88.0,
        "weighted_contribution": 26.40,
        "key_drivers": ["14 publications in recent 3-year window", "32 avg citations"]
      },
      {
        "pillar_name": "Patent Strength",
        "weight_percentage": 20.0,
        "score": 82.5,
        "weighted_contribution": 16.50,
        "key_drivers": ["Moderate assignee HHI (1850)", "High active filing velocity"]
      },
      {
        "pillar_name": "Technology Maturity (TRL)",
        "weight_percentage": 15.0,
        "score": 66.7,
        "weighted_contribution": 10.00,
        "key_drivers": ["Estimated TRL 6: Prototype model validated in environment"]
      },
      {
        "pillar_name": "Market Potential",
        "weight_percentage": 20.0,
        "score": 90.0,
        "weighted_contribution": 18.00,
        "key_drivers": ["24.5% 3-year CAGR across quantum computing"]
      },
      {
        "pillar_name": "Funding Relevance",
        "weight_percentage": 15.0,
        "score": 90.7,
        "weighted_contribution": 13.60,
        "key_drivers": ["$12.5M active funding pool across 4 grant solicitations"]
      }
    ],
    "estimated_trl": {
      "trl_level": 6,
      "title": "System/Subsystem Model Demonstration in Relevant Environment",
      "milestone_summary": "System prototypes operational; validated in high-fidelity conditions."
    },
    "confidence_score": 92.0
  }
  ```

---

## 6. Standardized Error Response Contract

Every API error follows this standardized schema:
```json
{
  "detail": "Descriptive error message explaining the failure",
  "status_code": 400,
  "error_code": "RESOURCE_NOT_FOUND"
}
```
*Standard Status Codes:*
- `400 Bad Request`: Validation failure or malformed payload.
- `401 Unauthorized`: Token missing, signature invalid, or expired.
- `403 Forbidden`: Insufficient role permissions or admin self-registration attempt.
- `404 Not Found`: Entity identifier does not exist.
- `422 Unprocessable Entity`: Pydantic field constraint violation.
- `500 Internal Server Error`: Unhandled backend exception.
