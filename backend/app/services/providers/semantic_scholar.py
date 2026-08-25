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


class SemanticScholarProvider(BaseResearchProvider):
    FIELDS = "title,abstract,authors,year,publicationDate,venue,externalIds,citationCount,fieldsOfStudy,s2FieldsOfStudy,url"

    def __init__(
        self,
        base_url: str = "https://api.semanticscholar.org/graph/v1",
        api_key: Optional[str] = None,
        timeout: float = 8.0,
        max_retries: int = 2
    ):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key or settings.SEMANTIC_SCHOLAR_API_KEY
        self._timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._max_retries = max_retries or settings.PROVIDER_MAX_RETRIES

    @property
    def name(self) -> str:
        return "semanticscholar"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "ResearchIntelligencePlatform/1.0",
            "Accept": "application/json"
        }
        if self._api_key:
            headers["x-api-key"] = self._api_key
        return headers

    def normalize_work(self, item: Dict[str, Any]) -> NormalizedPublication:
        """Transforms a Semantic Scholar Graph API paper object into a NormalizedPublication."""
        # 1. Title & Abstract
        title = item.get("title") or "Untitled Publication"
        abstract = item.get("abstract")

        # 2. Authors
        authors_list: List[NormalizedAuthor] = []
        raw_authors = item.get("authors", [])
        if isinstance(raw_authors, list):
            for a in raw_authors:
                name = a.get("name", "").strip()
                if name:
                    authors_list.append(NormalizedAuthor(name=name))

        authors_str = ", ".join([a.name for a in authors_list]) if authors_list else "Unknown Author"

        # 3. DOI & External IDs
        external_ids = item.get("externalIds") or {}
        raw_doi = external_ids.get("DOI") or item.get("doi")
        clean_doi = normalize_doi(raw_doi)
        paper_id = item.get("paperId")

        # 4. Publication Date & Year
        pub_date_str = item.get("publicationDate")
        pub_datetime = None
        if pub_date_str:
            try:
                pub_datetime = datetime.strptime(pub_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        year = item.get("year")

        # 5. Venue
        venue = item.get("venue")

        # 6. Citations & Domains & Keywords
        citation_count = item.get("citationCount", 0)

        # Primary Domain from fieldsOfStudy or s2FieldsOfStudy
        primary_domain = None
        s2_fields = item.get("s2FieldsOfStudy", [])
        if s2_fields and isinstance(s2_fields, list):
            primary_domain = s2_fields[0].get("category")
        if not primary_domain:
            fields = item.get("fieldsOfStudy", [])
            if fields and isinstance(fields, list):
                primary_domain = fields[0]

        keywords: List[str] = []
        if isinstance(s2_fields, list):
            for f in s2_fields:
                cat = f.get("category")
                if cat and cat not in keywords:
                    keywords.append(cat)
        elif isinstance(item.get("fieldsOfStudy"), list):
            keywords = [f for f in item.get("fieldsOfStudy") if isinstance(f, str)]

        url = item.get("url") or (f"https://doi.org/{clean_doi}" if clean_doi else None)

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
            source="semanticscholar",
            external_id=paper_id,
            url=url,
            raw_payload=item
        )

    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(self._max_retries + 1):
                try:
                    resp = await client.get(url, params=params, headers=headers)
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
                                message=f"Semantic Scholar HTTP {resp.status_code}: {resp.text[:200]}",
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
                            message=f"Semantic Scholar network error: {str(e)}",
                            provider_name=self.name,
                            details=str(e)
                        )
        return {}

    async def fetch_by_doi(self, doi: str) -> Optional[NormalizedPublication]:
        clean_doi = normalize_doi(doi)
        if not clean_doi:
            return None
        try:
            data = await self._request(f"paper/DOI:{clean_doi}", params={"fields": self.FIELDS})
            return self.normalize_work(data)
        except ProviderNotFoundException:
            return None

    async def search_publications(self, query: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request("paper/search", params={"query": query, "limit": limit, "fields": self.FIELDS})
            items = data.get("data", [])
            return [self.normalize_work(item) for item in items]
        except ProviderNotFoundException:
            return []

    async def fetch_by_author(self, author_identifier: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request(
                f"author/{author_identifier}/papers",
                params={"limit": limit, "fields": self.FIELDS}
            )
            items = data.get("data", [])
            return [self.normalize_work(item) for item in items]
        except ProviderNotFoundException:
            return []
