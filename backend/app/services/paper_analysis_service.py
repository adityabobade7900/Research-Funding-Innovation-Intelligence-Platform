import re
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    EntityNotFoundException,
    InsufficientContentException,
    ProviderServiceException,
)
from app.schemas.publication import PaperAnalysisResponse
from app.services.publication_service import PublicationService

logger = logging.getLogger(__name__)


# =====================================================================
# Abstract Analyzer Interface
# =====================================================================

class BasePaperAnalyzer(ABC):
    """Abstract base class for research paper analysis engines."""

    @abstractmethod
    async def analyze(
        self,
        title: str,
        abstract: str,
        authors: Optional[str] = None,
        venue: Optional[str] = None,
        primary_domain: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes research paper content and returns structured facets:
        - problem_statement
        - methodology
        - findings_contributions
        - limitations
        - future_research_directions
        - key_insights
        - confidence_score
        - analysis_source
        - provider
        """
        pass


# =====================================================================
# NLP Heuristic / Semantic Rule-Based Analyzer
# =====================================================================

class NLPHeuristicPaperAnalyzer(BasePaperAnalyzer):
    """
    Deterministic scientific discourse analyzer.
    Extracts the 5 required facets from paper abstract and metadata
    using semantic discourse markers and domain heuristics.
    """

    PROBLEM_MARKERS = [
        "challenge", "problem", "bottleneck", "lack of", "hindered by",
        "struggle to", "remains a", "limited by", "issue", "difficult to",
        "vulnerable to", "addresses the need", "gap in", "inability to",
        "fails to", "impediment", "obstacle", "unresolved"
    ]

    METHOD_MARKERS = [
        "we propose", "we introduce", "we design", "we implement", "our approach",
        "methodology", "framework", "architecture", "algorithm", "model",
        "pipeline", "experiments", "evaluation", "utilizes", "employs",
        "dataset", "trained on", "pre-trained", "we develop", "in this work, we"
    ]

    FINDING_MARKERS = [
        "we demonstrate", "we find", "results show", "improves", "achieves",
        "outperforms", "reduces", "reduction of", "accuracy", "fidelity",
        "significant", "superior", "contributes", "demonstration of",
        "benchmark", "yields", "evaluations demonstrate", "surpasses"
    ]

    LIMITATION_MARKERS = [
        "limitation", "constrained by", "drawback", "bottleneck", "trade-off",
        "tradeoff", "overhead", "high latency", "memory footprint",
        "memory requirement", "vulnerability to", "bloat", "restricted to",
        "however", "nonetheless", "despite", "fails when", "at the cost of"
    ]

    FUTURE_MARKERS = [
        "future work", "future research", "will explore", "plans to",
        "should prioritize", "directions include", "promising avenue",
        "ongoing work", "open questions", "next steps", "further study",
        "extensions of this"
    ]

    def _split_sentences(self, text: str) -> List[str]:
        """Splits abstract text into distinct sentences using regex."""
        raw_sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in raw_sentences if len(s.strip()) > 15]

    async def analyze(
        self,
        title: str,
        abstract: str,
        authors: Optional[str] = None,
        venue: Optional[str] = None,
        primary_domain: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        sentences = self._split_sentences(abstract)

        problem_matches: List[str] = []
        method_matches: List[str] = []
        finding_matches: List[str] = []
        limitation_matches: List[str] = []
        future_matches: List[str] = []

        for idx, sentence in enumerate(sentences):
            s_lower = sentence.lower()

            # 1. Future Work priority
            if any(marker in s_lower for marker in self.FUTURE_MARKERS):
                future_matches.append(sentence)
                continue

            # 2. Limitation of paper's own work (typically non-initial sentence or starting with contrast marker)
            is_contrast = s_lower.startswith(("however", "nonetheless", "despite", "although", "a limitation", "one limitation"))
            has_own_constraint = any(marker in s_lower for marker in [
                "constrained by", "drawback", "bottleneck", "trade-off", "tradeoff",
                "memory requirement", "proof size bloat", "restricted to", "limitation of this work",
                "is constrained", "latency exceeding", "loss rates"
            ])
            if (is_contrast or has_own_constraint) and idx > 0:
                limitation_matches.append(sentence)
                continue

            # 3. Methodology priority
            if any(marker in s_lower for marker in ["we propose", "we introduce", "we design", "we implement", "our methodology", "our approach", "the proposed framework", "in this work", "architecture pre-trained", "we develop"]):
                method_matches.append(sentence)
                continue

            # 4. Findings / Contributions priority
            if any(marker in s_lower for marker in ["demonstrate", "we find", "results show", "improves", "outperforms", "reduction of", "accuracy", "fidelity", "evaluations demonstrate", "sub-millisecond verification"]):
                finding_matches.append(sentence)
                continue

            # 5. Problem Statement priority (initial problem/challenge)
            if any(marker in s_lower for marker in self.PROBLEM_MARKERS) or idx == 0:
                problem_matches.append(sentence)
                continue

            # Fallback based on position in abstract if unclassified
            # Sentences are typically structured: Background/Problem -> Method -> Result -> Discussion


        # 1. Problem Statement
        if problem_matches:
            problem_statement = " ".join(problem_matches[:2])
        elif len(sentences) >= 1:
            problem_statement = f"The research addresses core technical challenges in {primary_domain or 'the target field'}: {sentences[0]}"
        else:
            problem_statement = f"Addresses scientific problems related to {title}."

        # 2. Methodology
        if method_matches:
            methodology = " ".join(method_matches[:2])
        elif len(sentences) >= 2:
            methodology = f"The authors employ an experimental framework centered on: {sentences[1]}"
        else:
            kw_str = ", ".join(keywords[:4]) if keywords else "computational/experimental models"
            methodology = f"Investigation based on techniques including {kw_str} applied to {title}."

        # 3. Findings / Contributions
        if finding_matches:
            findings_contributions = " ".join(finding_matches[:2])
        elif len(sentences) >= 3:
            findings_contributions = f"Key outcomes reported: {sentences[2]}"
        else:
            findings_contributions = f"Contributes empirical and technical advancements in {primary_domain or 'the respective domain'} as validated by the authors."

        # 4. Limitations (strictly honest: do not hallucinate)
        if limitation_matches:
            limitations = " ".join(limitation_matches[:2])
        else:
            limitations = (
                "Explicit limitations were not stated in the available abstract/metadata. "
                "Further operational constraints (such as computational overhead, scaling limits, "
                "or sample specificity) require examination of the full-text publication."
            )

        # 5. Future Research Directions (strictly honest)
        if future_matches:
            future_research_directions = " ".join(future_matches[:2])
        else:
            future_research_directions = (
                "Future research directions were not explicitly delineated in the available abstract. "
                "Expected follow-up avenues include expanding evaluation benchmarks, optimizing computational "
                "complexity, and extending cross-domain validation."
            )

        # Key Insights
        key_insights: List[str] = []
        if method_matches:
            key_insights.append(f"Approach: {method_matches[0]}")
        if finding_matches:
            key_insights.append(f"Impact: {finding_matches[0]}")
        if limitation_matches:
            key_insights.append(f"Constraint: {limitation_matches[0]}")
        elif future_matches:
            key_insights.append(f"Next Horizon: {future_matches[0]}")

        if not key_insights and sentences:
            key_insights.append(f"Core Focus: {sentences[0]}")
            if len(sentences) > 1:
                key_insights.append(f"Reported Evidence: {sentences[-1]}")

        # Confidence calculation
        detected_facets = sum([
            bool(problem_matches),
            bool(method_matches),
            bool(finding_matches),
            bool(limitation_matches),
            bool(future_matches),
        ])
        base_confidence = 0.60 + (0.07 * detected_facets)
        confidence_score = min(round(base_confidence, 2), 0.95)

        return {
            "problem_statement": problem_statement,
            "methodology": methodology,
            "findings_contributions": findings_contributions,
            "limitations": limitations,
            "future_research_directions": future_research_directions,
            "confidence_score": confidence_score,
            "analysis_source": "title_and_abstract",
            "provider": "nlp-heuristic-analyzer",
            "key_insights": key_insights,
        }


# =====================================================================
# LLM Paper Analyzer (Gemini / OpenAI API Integration)
# =====================================================================

class LLMPaperAnalyzer(BasePaperAnalyzer):
    """
    LLM-powered research paper analyzer using Gemini or OpenAI APIs.
    Grounded exclusively in the supplied publication title, abstract, and metadata.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or "gemini").lower()
        self.gemini_key = settings.GEMINI_API_KEY
        self.openai_key = settings.OPENAI_API_KEY

    async def analyze(
        self,
        title: str,
        abstract: str,
        authors: Optional[str] = None,
        venue: Optional[str] = None,
        primary_domain: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if self.provider == "openai" and self.openai_key:
            return await self._call_openai(title, abstract, authors, venue, primary_domain, keywords)
        elif self.gemini_key:
            return await self._call_gemini(title, abstract, authors, venue, primary_domain, keywords)
        else:
            raise ProviderServiceException(
                message=f"Live AI provider '{self.provider}' is not configured. Missing API credentials."
            )

    async def _call_gemini(
        self,
        title: str,
        abstract: str,
        authors: Optional[str],
        venue: Optional[str],
        primary_domain: Optional[str],
        keywords: Optional[List[str]],
    ) -> Dict[str, Any]:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
        prompt = self._build_prompt(title, abstract, authors, venue, primary_domain, keywords)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(endpoint, json=payload)
                if res.status_code != 200:
                    logger.error(f"Gemini API returned status {res.status_code}: {res.text}")
                    raise ProviderServiceException(message=f"Gemini AI provider returned HTTP {res.status_code}")

                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                result = json.loads(raw_text)
                result["provider"] = "gemini-1.5-flash"
                result["analysis_source"] = "title_and_abstract"
                return result
        except (httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error querying Gemini API: {str(e)}")
            raise ProviderServiceException(message="Failed to obtain response from Gemini AI provider")

    async def _call_openai(
        self,
        title: str,
        abstract: str,
        authors: Optional[str],
        venue: Optional[str],
        primary_domain: Optional[str],
        keywords: Optional[List[str]],
    ) -> Dict[str, Any]:
        endpoint = "https://api.openai.com/v1/chat/completions"
        prompt = self._build_prompt(title, abstract, authors, venue, primary_domain, keywords)

        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a scientific research assistant specializing in rigorous paper analysis. Respond strictly in valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(endpoint, headers=headers, json=payload)
                if res.status_code != 200:
                    logger.error(f"OpenAI API returned status {res.status_code}: {res.text}")
                    raise ProviderServiceException(message=f"OpenAI provider returned HTTP {res.status_code}")

                data = res.json()
                raw_text = data["choices"][0]["message"]["content"]
                result = json.loads(raw_text)
                result["provider"] = "gpt-4o-mini"
                result["analysis_source"] = "title_and_abstract"
                return result
        except (httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error querying OpenAI API: {str(e)}")
            raise ProviderServiceException(message="Failed to obtain response from OpenAI provider")

    def _build_prompt(
        self,
        title: str,
        abstract: str,
        authors: Optional[str],
        venue: Optional[str],
        primary_domain: Optional[str],
        keywords: Optional[List[str]],
    ) -> str:
        kw_str = ", ".join(keywords) if keywords else "None"
        return f"""Analyze the following scientific research paper metadata and abstract.
Do NOT invent or hallucinate information not supported by the provided text.
Do NOT discuss business models, commercialization, venture capital, or funding.
Focus exclusively on scientific and technical understanding of the paper.

PAPER DETAILS:
Title: {title}
Authors: {authors or 'N/A'}
Venue: {venue or 'N/A'}
Domain: {primary_domain or 'N/A'}
Keywords: {kw_str}
Abstract:
{abstract}

REQUIRED JSON STRUCTURE:
{{
  "problem_statement": "What specific research problem/gap does this paper address?",
  "methodology": "What approach, algorithm, architecture, dataset, or experimental methods are used?",
  "findings_contributions": "What did the authors discover, demonstrate, or contribute? Include specific quantitative outcomes if present.",
  "limitations": "What limitations are explicitly mentioned or evident from the scope? If none are mentioned, state that explicit limitations were not identified in the abstract.",
  "future_research_directions": "What future work is suggested? If none is mentioned, state that future work was not identified in the abstract.",
  "confidence_score": 0.90,
  "key_insights": ["Key point 1", "Key point 2", "Key point 3"]
}}
"""


# =====================================================================
# Mock Paper Analyzer (For Automated Testing)
# =====================================================================

class MockPaperAnalyzer(BasePaperAnalyzer):
    """Configurable mock analyzer for testing edge cases and failure modes."""

    def __init__(self, simulate_failure: bool = False, custom_facets: Optional[Dict[str, Any]] = None):
        self.simulate_failure = simulate_failure
        self.custom_facets = custom_facets

    async def analyze(
        self,
        title: str,
        abstract: str,
        authors: Optional[str] = None,
        venue: Optional[str] = None,
        primary_domain: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if self.simulate_failure:
            raise ProviderServiceException(message="Simulated upstream AI provider connection failure")

        if self.custom_facets:
            return self.custom_facets

        return {
            "problem_statement": f"Investigates fundamental constraints in {title}.",
            "methodology": "Dual-channel quantitative modeling with empirical benchmarking.",
            "findings_contributions": "Demonstrates statistically significant improvements over existing baselines.",
            "limitations": "Evaluations are limited to synthetic datasets and controlled laboratory settings.",
            "future_research_directions": "Scaling experiments to heterogeneous multi-cluster production environments.",
            "confidence_score": 0.92,
            "analysis_source": "title_and_abstract",
            "provider": "mock-analyzer",
            "key_insights": ["Achieved benchmark improvements", "Evaluated on synthetic data"],
        }


# =====================================================================
# Paper Analysis Service
# =====================================================================

class PaperAnalysisService:
    """Orchestrates research paper analysis across providers."""

    @classmethod
    async def analyze_publication(
        cls,
        pub_id: int,
        user_id: int,
        is_admin: bool,
        db: AsyncSession,
        provider_override: Optional[str] = None,
        analyzer_instance: Optional[BasePaperAnalyzer] = None,
    ) -> PaperAnalysisResponse:
        """
        Retrieves a publication, validates content sufficiency,
        and analyzes the paper into five scientific facets.
        """
        pub = await PublicationService.get_publication(pub_id=pub_id, db=db)
        if not pub:
            raise EntityNotFoundException(message=f"Publication with ID {pub_id} not found")

        # Validate content sufficiency
        abstract = pub.abstract.strip() if pub.abstract else ""
        word_count = len(abstract.split())
        if not abstract or word_count < 10:
            raise InsufficientContentException(
                message=f"Publication abstract is insufficient for scientific analysis (found {word_count} words; minimum 10 words required). Please update the publication abstract."
            )

        # Select analyzer engine
        analyzer: BasePaperAnalyzer
        if analyzer_instance is not None:
            analyzer = analyzer_instance
        elif provider_override in ["gemini", "openai"]:
            analyzer = LLMPaperAnalyzer(provider=provider_override)
        elif provider_override == "mock":
            analyzer = MockPaperAnalyzer()
        elif settings.GEMINI_API_KEY:
            analyzer = LLMPaperAnalyzer(provider="gemini")
        elif settings.OPENAI_API_KEY:
            analyzer = LLMPaperAnalyzer(provider="openai")
        else:
            analyzer = NLPHeuristicPaperAnalyzer()

        # Extract keyword strings
        keyword_list = [k.keyword for k in pub.keywords] if pub.keywords else []

        # Execute analysis
        raw_result = await analyzer.analyze(
            title=pub.title,
            abstract=abstract,
            authors=pub.authors,
            venue=pub.venue,
            primary_domain=pub.primary_domain,
            keywords=keyword_list,
        )

        return PaperAnalysisResponse(
            publication_id=pub.id,
            title=pub.title,
            doi=pub.doi,
            primary_domain=pub.primary_domain,
            authors=pub.authors,
            problem_statement=raw_result.get("problem_statement", ""),
            methodology=raw_result.get("methodology", ""),
            findings_contributions=raw_result.get("findings_contributions", ""),
            limitations=raw_result.get("limitations", ""),
            future_research_directions=raw_result.get("future_research_directions", ""),
            confidence_score=float(raw_result.get("confidence_score", 0.85)),
            analysis_source=raw_result.get("analysis_source", "title_and_abstract"),
            analyzed_at=datetime.now(timezone.utc),
            provider=raw_result.get("provider", "nlp-heuristic-analyzer"),
            key_insights=raw_result.get("key_insights", []),
        )
