import httpx
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.services.providers.base import (
    BaseResearchProvider,
    NormalizedPublication,
    NormalizedAuthor,
    normalize_doi,
    ProviderException,
    ProviderTimeoutException,
    ProviderRateLimitException,
    ProviderNotFoundException,
)


class OpenAlexProvider(BaseResearchProvider):
    def __init__(
        self,
        base_url: str = "https://api.openalex.org",
        email: Optional[str] = None,
        timeout: float = 8.0,
        max_retries: int = 2
    ):
        self._base_url = base_url.rstrip("/")
        self._email = email or settings.OPENALEX_EMAIL
        self._timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._max_retries = max_retries or settings.PROVIDER_MAX_RETRIES

    @property
    def name(self) -> str:
        return "openalex"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "ResearchIntelligencePlatform/1.0",
            "Accept": "application/json"
        }
        return headers

    def _get_params(self, extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if self._email:
            params["mailto"] = self._email
        if extra_params:
            params.update(extra_params)
        return params

    def _reconstruct_abstract(self, inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
        """Reconstructs full text abstract from OpenAlex inverted index map."""
        if not inverted_index or not isinstance(inverted_index, dict):
            return None
        try:
            position_word_pairs = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    position_word_pairs.append((pos, word))
            position_word_pairs.sort(key=lambda x: x[0])
            return " ".join([word for _, word in position_word_pairs])
        except Exception:
            return None

    def normalize_work(self, item: Dict[str, Any]) -> NormalizedPublication:
        """Transforms an OpenAlex work JSON object into a NormalizedPublication."""
        # 1. Title & Abstract
        title = item.get("title") or item.get("display_name") or "Untitled Publication"
        abstract = self._reconstruct_abstract(item.get("abstract_inverted_index"))

        # 2. Authors
        authors_list: List[NormalizedAuthor] = []
        raw_authorships = item.get("authorships", [])
        if isinstance(raw_authorships, list):
            for authorship in raw_authorships:
                author_obj = authorship.get("author", {})
                author_name = author_obj.get("display_name", "").strip()
                if author_name:
                    orcid = author_obj.get("orcid")
                    affiliations = authorship.get("institutions", [])
                    affiliation_name = affiliations[0].get("display_name") if affiliations else None
                    authors_list.append(
                        NormalizedAuthor(name=author_name, orcid=orcid, affiliation=affiliation_name)
                    )

        authors_str = ", ".join([a.name for a in authors_list]) if authors_list else "Unknown Author"

        # 3. DOI & IDs
        raw_doi = item.get("doi")
        clean_doi = normalize_doi(raw_doi)
        openalex_id = item.get("id")  # e.g., "https://openalex.org/W2741809807"
        if openalex_id and "/" in openalex_id:
            openalex_id = openalex_id.split("/")[-1]

        # 4. Publication Date & Year
        pub_date_str = item.get("publication_date")
        pub_datetime = None
        if pub_date_str:
            try:
                pub_datetime = datetime.strptime(pub_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        year = item.get("publication_year")

        # 5. Venue / Host Location
        primary_loc = item.get("primary_location") or {}
        source_obj = primary_loc.get("source") or {}
        venue = source_obj.get("display_name") or item.get("host_venue", {}).get("name")

        # 6. Citations & Domains & Keywords
        citation_count = item.get("cited_by_count", 0)

        # Primary Domain
        primary_topic = item.get("primary_topic") or {}
        domain_obj = primary_topic.get("domain") or {}
        primary_domain = domain_obj.get("display_name")
        if not primary_domain:
            field_obj = primary_topic.get("field") or {}
            primary_domain = field_obj.get("display_name")

        # Keywords from concepts
        keywords: List[str] = []
        concepts = item.get("concepts", [])
        if isinstance(concepts, list):
            for c in concepts:
                c_name = c.get("display_name")
                c_score = c.get("score", 0.0)
                if c_name and c_score >= 0.3:
                    keywords.append(c_name)

        landing_url = primary_loc.get("landing_page_url") or item.get("doi")

        return NormalizedPublication(
            title=title,
            authors=authors_str,
            authors_list=authors_list,
            abstract=abstract,
            publication_date=pub_datetime,
            year=year,
            venue=venue,
            doi=clean_doi,
            citation_count=citation_count if citation_count is not None else 0,
            primary_domain=primary_domain,
            keywords=keywords,
            source="openalex",
            external_id=openalex_id,
            url=landing_url,
            raw_payload=item
        )

    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        merged_params = self._get_params(params)
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(self._max_retries + 1):
                try:
                    resp = await client.get(url, params=merged_params, headers=headers)
                    if resp.status_code == 200:
                        return resp.json()
                    elif resp.status_code == 404:
                        raise ProviderNotFoundException(provider_name=self.name, identifier=endpoint)
                    elif resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        raise ProviderRateLimitException(
                            provider_name=self.name,
                            retry_after=int(retry_after) if retry_after and retry_after.isdigit() else None
                        )
                    else:
                        if attempt == self._max_retries:
                            raise ProviderException(
                                message=f"OpenAlex HTTP {resp.status_code}: {resp.text[:200]}",
                                provider_name=self.name,
                                status_code=resp.status_code
                            )
                except httpx.TimeoutException:
                    if attempt == self._max_retries:
                        raise ProviderTimeoutException(provider_name=self.name, timeout_seconds=self._timeout)
                except (ProviderNotFoundException, ProviderRateLimitException):
                    raise
                except Exception as e:
                    if attempt == self._max_retries:
                        raise ProviderException(
                            message=f"OpenAlex network error: {str(e)}",
                            provider_name=self.name,
                            details=str(e)
                        )
        return {}

    async def fetch_by_doi(self, doi: str) -> Optional[NormalizedPublication]:
        clean_doi = normalize_doi(doi)
        if not clean_doi:
            return None
        try:
            data = await self._request(f"works/https://doi.org/{clean_doi}")
            return self.normalize_work(data)
        except ProviderNotFoundException:
            return None

    async def search_publications(self, query: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request("works", params={"search": query, "per-page": limit})
            results = data.get("results", [])
            return [self.normalize_work(item) for item in results]
        except ProviderNotFoundException:
            return []

    async def fetch_by_author(self, author_identifier: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request("works", params={"filter": f"author.id:{author_identifier}", "per-page": limit})
            results = data.get("results", [])
            return [self.normalize_work(item) for item in results]
        except ProviderNotFoundException:
            return []
