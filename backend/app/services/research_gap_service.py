import logging
from collections import defaultdict
from typing import List, Optional, Dict, Any, Set
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.publication import Publication
from app.schemas.research_intelligence import (
    ResearchGapItem,
    ResearchGapsResponse
)
from app.services.paper_analysis_service import NLPHeuristicPaperAnalyzer

logger = logging.getLogger(__name__)


class ResearchGapService:
    """
    Synthesizes and discovers macro-corpus research gaps across indexed publications.
    Extracts recurring limitations, unaddressed problem statements, and explicit future directions
    grounded strictly in empirical publication content.
    """

    MIN_CORPUS_SIZE: int = 2

    @classmethod
    async def get_research_gaps(
        cls,
        domain: Optional[str] = None,
        min_confidence: float = 0.6,
        limit: int = 10,
        db: AsyncSession = None
    ) -> ResearchGapsResponse:
        """
        Discovers cross-paper scientific research gaps across the publication corpus.
        Returns an INSUFFICIENT_DATA status if the corpus has fewer than MIN_CORPUS_SIZE papers.
        """
        stmt = select(Publication).options(selectinload(Publication.keywords))
        if domain:
            stmt = stmt.where(Publication.primary_domain.ilike(f"%{domain.strip()}%"))

        res = await db.execute(stmt)
        publications = list(res.scalars().all())

        # 1. Guardrail against insufficient corpus size
        if len(publications) < cls.MIN_CORPUS_SIZE:
            return ResearchGapsResponse(
                total_gaps=0,
                status="INSUFFICIENT_DATA",
                gaps=[],
                message=(
                    f"Corpus contains insufficient publications ({len(publications)} found; minimum "
                    f"{cls.MIN_CORPUS_SIZE} required) to reliably synthesize cross-paper research gaps."
                )
            )

        # 2. Group publications by domain
        domain_groups: Dict[str, List[Publication]] = defaultdict(list)
        for pub in publications:
            dom = pub.primary_domain or "Interdisciplinary Sciences"
            domain_groups[dom].append(pub)

        analyzer = NLPHeuristicPaperAnalyzer()
        gaps: List[ResearchGapItem] = []

        # 3. Analyze each domain group for convergent gaps
        for dom_name, pub_list in domain_groups.items():
            domain_limitation_sentences: List[Tuple[str, int]] = []
            domain_future_sentences: List[Tuple[str, int]] = []
            domain_keywords: Set[str] = set()

            for pub in pub_list:
                for kw in pub.keywords:
                    domain_keywords.add(kw.keyword)

                if pub.abstract and len(pub.abstract.split()) >= 10:
                    analysis = await analyzer.analyze(
                        title=pub.title,
                        abstract=pub.abstract,
                        authors=pub.authors,
                        venue=pub.venue,
                        primary_domain=pub.primary_domain,
                        keywords=[k.keyword for k in pub.keywords]
                    )

                    lim = analysis.get("limitations", "")
                    fut = analysis.get("future_research_directions", "")

                    if lim and "explicit limitations were not stated" not in lim.lower():
                        domain_limitation_sentences.append((lim, pub.id))
                    if fut and "future research directions were not explicitly delineated" not in fut.lower():
                        domain_future_sentences.append((fut, pub.id))

            # If no limitations or future directions found in this domain
            if not domain_limitation_sentences and not domain_future_sentences:
                continue

            # Synthesize grounded gap
            supporting_pub_ids = list(dict.fromkeys(
                [pid for _, pid in domain_limitation_sentences] +
                [pid for _, pid in domain_future_sentences]
            ))

            evidence_count = len(domain_limitation_sentences) + len(domain_future_sentences)

            # Construct representative gap title and evidence narrative
            sample_limitation = domain_limitation_sentences[0][0] if domain_limitation_sentences else ""
            sample_future = domain_future_sentences[0][0] if domain_future_sentences else ""

            # Extract key topic nouns
            kw_sample = list(domain_keywords)[:4]
            kw_title = f"{kw_sample[0]} & {kw_sample[1]}" if len(kw_sample) >= 2 else (kw_sample[0] if kw_sample else dom_name)

            gap_title = f"Unresolved Bottlenecks in {kw_title} ({dom_name})"

            evidence_narrative = (
                f"Cross-publication analysis across {len(supporting_pub_ids)} paper(s) in {dom_name} "
                f"demonstrates explicit consensus on critical constraints: "
            )
            if sample_limitation:
                evidence_narrative += f"Identified constraint: '{sample_limitation}' "
            if sample_future:
                evidence_narrative += f"Suggested unaddressed trajectory: '{sample_future}'"

            confidence = min(0.95, round(0.70 + (0.05 * len(supporting_pub_ids)), 2))

            if confidence >= min_confidence:
                gaps.append(
                    ResearchGapItem(
                        gap=gap_title,
                        domain=dom_name,
                        evidence_count=evidence_count,
                        supporting_keywords=kw_sample,
                        supporting_publications=supporting_pub_ids,
                        evidence=evidence_narrative,
                        confidence=confidence
                    )
                )

        if not gaps:
            return ResearchGapsResponse(
                total_gaps=0,
                status="NO_GAPS_IDENTIFIED",
                gaps=[],
                message="No explicit research gaps or limitations were delineated across the current publication corpus."
            )

        gaps.sort(key=lambda g: (g.evidence_count, g.confidence), reverse=True)
        top_gaps = gaps[:limit]

        return ResearchGapsResponse(
            total_gaps=len(gaps),
            status="SUCCESS",
            gaps=top_gaps,
            message=f"Successfully synthesized {len(top_gaps)} scientific research gap(s) across {len(publications)} publications."
        )
