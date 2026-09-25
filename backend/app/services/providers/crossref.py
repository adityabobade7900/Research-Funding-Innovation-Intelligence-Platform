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


class CrossrefProvider(BaseResearchProvider):
    def __init__(
        self,
        base_url: str = "https://api.crossref.org",
        mailto: Optional[str] = None,
        timeout: float = 8.0,
        max_retries: int = 2
    ):
        self._base_url = base_url.rstrip("/")
        self._mailto = mailto or settings.CROSSREF_MAILTO
        self._timeout = timeout or settings.PROVIDER_TIMEOUT_SECONDS
        self._max_retries = max_retries or settings.PROVIDER_MAX_RETRIES

    @property
    def name(self) -> str:
        return "crossref"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": f"ResearchIntelligencePlatform/1.0 (mailto:{self._mailto or 'contact@university.edu'})",
            "Accept": "application/json"
        }
        return headers

    def normalize_work(self, item: Dict[str, Any]) -> NormalizedPublication:
        """Transforms a Crossref message work object into a NormalizedPublication."""
        # 1. Title
        title_list = item.get("title", [])
        title = title_list[0] if title_list and isinstance(title_list, list) else "Untitled Publication"

        # 2. Abstract
        abstract = item.get("abstract")
        if abstract and isinstance(abstract, str):
            # Clean possible JATS XML tags in abstract
            abstract = abstract.replace("<jats:p>", "").replace("</jats:p>", "").replace("<jats:sec>", "").replace("</jats:sec>", "").strip()

        # 3. Authors
        authors_list: List[NormalizedAuthor] = []
        raw_authors = item.get("author", [])
        if isinstance(raw_authors, list):
            for a in raw_authors:
                given = a.get("given", "").strip()
                family = a.get("family", "").strip()
                full_name = f"{given} {family}".strip() or a.get("name", "").strip()
                if full_name:
                    orcid = a.get("ORCID")
                    affil_list = a.get("affiliation", [])
                    affiliation_name = affil_list[0].get("name") if affil_list and isinstance(affil_list[0], dict) else None
                    authors_list.append(
                        NormalizedAuthor(name=full_name, orcid=orcid, affiliation=affiliation_name)
                    )

        authors_str = ", ".join([a.name for a in authors_list]) if authors_list else "Unknown Author"

        # 4. DOI & URL
        raw_doi = item.get("DOI")
        clean_doi = normalize_doi(raw_doi)
        url = item.get("URL") or (f"https://doi.org/{clean_doi}" if clean_doi else None)

        # 5. Venue
        container_list = item.get("container-title", [])
        venue = container_list[0] if container_list and isinstance(container_list, list) else None

        # 6. Publication Date
        pub_datetime = None
        year = None
        date_parts_holder = item.get("published-print") or item.get("published-online") or item.get("issued") or {}
        date_parts = date_parts_holder.get("date-parts", [[]])
        if date_parts and len(date_parts[0]) > 0:
            try:
                parts = date_parts[0]
                year = parts[0]
                month = parts[1] if len(parts) > 1 else 1
                day = parts[2] if len(parts) > 2 else 1
                pub_datetime = datetime(year, month, day, tzinfo=timezone.utc)
            except Exception:
                pass

        # 7. Citations & Keywords
        citation_count = item.get("is-referenced-by-count", 0)
        keywords = item.get("subject", []) or []

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
            primary_domain=None,
            keywords=keywords,
            source="crossref",
            external_id=clean_doi,
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
                                message=f"Crossref HTTP {resp.status_code}: {resp.text[:200]}",
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
                            message=f"Crossref network error: {str(e)}",
                            provider_name=self.name,
                            details=str(e)
                        )
        return {}

    async def fetch_by_doi(self, doi: str) -> Optional[NormalizedPublication]:
        clean_doi = normalize_doi(doi)
        if not clean_doi:
            return None
        try:
            data = await self._request(f"works/{clean_doi}")
            message = data.get("message", {})
            return self.normalize_work(message)
        except ProviderNotFoundException:
            return None

    async def search_publications(self, query: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request("works", params={"query": query, "rows": limit})
            items = data.get("message", {}).get("items", [])
            return [self.normalize_work(item) for item in items]
        except ProviderNotFoundException:
            return []

    async def fetch_by_author(self, author_identifier: str, limit: int = 20) -> List[NormalizedPublication]:
        try:
            data = await self._request("works", params={"query.author": author_identifier, "rows": limit})
            items = data.get("message", {}).get("items", [])
            return [self.normalize_work(item) for item in items]
        except ProviderNotFoundException:
            return []
