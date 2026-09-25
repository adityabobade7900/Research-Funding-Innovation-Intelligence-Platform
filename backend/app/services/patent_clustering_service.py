import re
from collections import Counter
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from app.models.patent import Patent, profile_patents
from app.schemas.patent_intelligence import (
    PatentClusterMember,
    PatentClusterItem,
    PatentClusteringResponse,
)


class PatentClusteringService:
    """
    Unsupervised Machine Learning Patent Clustering Engine.
    Employs TF-IDF Vectorization and K-Means Centroid Partitioning over patent titles,
    abstracts, technology domains, classifications, and assignees.
    """

    @classmethod
    def _apply_base_filters(
        cls,
        query,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        classification: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        profile_id: Optional[int] = None,
    ):
        if profile_id is not None:
            query = query.join(profile_patents, Patent.id == profile_patents.c.patent_id).filter(
                profile_patents.c.profile_id == profile_id
            )

        if start_year is not None:
            query = query.filter(
                or_(
                    func.extract("year", Patent.filing_date) >= start_year,
                    func.extract("year", Patent.publication_date) >= start_year,
                )
            )

        if end_year is not None:
            query = query.filter(
                or_(
                    func.extract("year", Patent.filing_date) <= end_year,
                    func.extract("year", Patent.publication_date) <= end_year,
                )
            )

        if domain:
            query = query.filter(Patent.technology_domain.ilike(f"%{domain}%"))

        if classification:
            query = query.filter(Patent.patent_classification.ilike(f"%{classification}%"))

        if assignee:
            query = query.filter(Patent.assignee.ilike(f"%{assignee}%"))

        if jurisdiction:
            code = jurisdiction.strip().upper()
            query = query.filter(Patent.patent_number.ilike(f"{code}%"))

        return query

    @classmethod
    async def cluster_patents(
        cls,
        db: AsyncSession,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        domain: Optional[str] = None,
        classification: Optional[str] = None,
        assignee: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        k: Optional[int] = None,
        profile_id: Optional[int] = None,
    ) -> PatentClusteringResponse:
        """
        Executes TF-IDF + K-Means clustering across indexed patents matching the requested filters.
        """
        stmt = select(Patent)
        stmt = cls._apply_base_filters(
            stmt,
            start_year=start_year,
            end_year=end_year,
            domain=domain,
            classification=classification,
            assignee=assignee,
            jurisdiction=jurisdiction,
            profile_id=profile_id,
        )
        stmt = stmt.order_by(Patent.id)
        res = await db.execute(stmt)
        patents = list(res.scalars().all())

        total_patents = len(patents)

        # Edge Case 1: 0 Patents
        if total_patents == 0:
            return PatentClusteringResponse(
                total_patents=0,
                total_clusters=0,
                algorithm="TF-IDF Vectorization + K-Means Clustering",
                k_requested=k,
                clusters=[],
                disclaimer="No patents matched the specified filter criteria; 0 clusters formed."
            )

        # Edge Case 2: 1 Patent (Singleton Cluster)
        if total_patents == 1:
            p = patents[0]
            dom = p.technology_domain or "General Technology"
            title_words = [w.lower() for w in re.findall(r"\b[A-Za-z]{3,}\b", p.title)]
            dom_words = [w.lower() for w in re.findall(r"\b[A-Za-z]{3,}\b", dom)]
            dominant_terms = list(dict.fromkeys(title_words + dom_words))[:5] or ["patent", "technology"]
            top_term_str = ", ".join(dominant_terms[:2])
            cluster_name = f"{dom} ({top_term_str})" if top_term_str else dom

            member = PatentClusterMember(
                patent_id=p.id,
                patent_number=p.patent_number,
                title=p.title,
                assignee=p.assignee,
                technology_domain=p.technology_domain,
                patent_classification=p.patent_classification,
                citation_count=p.citation_count,
                distance_to_centroid=0.0,
                explanation="Singleton cluster containing sole patent in the evaluated corpus.",
            )

            item = PatentClusterItem(
                cluster_id=1,
                cluster_name=cluster_name,
                technology_domain=dom,
                patent_count=1,
                share_percentage=100.0,
                dominant_terms=dominant_terms,
                average_citations=float(p.citation_count),
                representative_patents=[member],
                description=f"Isolated technology node centered on '{p.title}'.",
            )

            return PatentClusteringResponse(
                total_patents=1,
                total_clusters=1,
                algorithm="TF-IDF Vectorization (Singleton Partition)",
                k_requested=k,
                clusters=[item],
                disclaimer="Single-element corpus formed a singleton cluster without iterative partitioning."
            )

        # Build text corpus for TF-IDF
        documents: List[str] = []
        for p in patents:
            parts = [
                p.title or "",
                p.abstract or "",
                p.technology_domain or "",
                p.patent_classification or "",
                p.assignee or "",
            ]
            documents.append(" ".join(filter(None, parts)))

        # Vectorize using scikit-learn TF-IDF
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=500,
            ngram_range=(1, 2),
            min_df=1,
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()

        # Determine sensible K
        if k is not None and 1 <= k <= total_patents:
            num_clusters = k
        else:
            # Heuristic: min(max(2, round(sqrt(N))), min(6, N))
            num_clusters = min(max(2, int(round(total_patents ** 0.5))), min(6, total_patents))

        # Perform K-Means Clustering
        kmeans = KMeans(
            n_clusters=num_clusters,
            random_state=42,
            n_init=10,
            max_iter=300
        )
        kmeans.fit(tfidf_matrix)
        cluster_labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        # Group patents by assigned cluster
        clusters_dict: Dict[int, List[Tuple[Patent, float]]] = {i: [] for i in range(num_clusters)}

        dense_matrix = tfidf_matrix.toarray()
        for idx, (p, label) in enumerate(zip(patents, cluster_labels)):
            # Calculate Euclidean distance to cluster centroid
            centroid = centroids[label]
            vec = dense_matrix[idx]
            dist = float(np.linalg.norm(vec - centroid))
            clusters_dict[label].append((p, dist))

        # Order centroids to extract top terms
        order_centroids = centroids.argsort()[:, ::-1]

        cluster_items: List[PatentClusterItem] = []

        for cid in range(num_clusters):
            members_with_dist = clusters_dict[cid]
            if not members_with_dist:
                continue

            p_count = len(members_with_dist)
            share_pct = round((p_count / float(total_patents)) * 100.0, 2)

            # Top terms from centroid
            top_term_indices = order_centroids[cid][:8]
            dominant_terms: List[str] = []
            for term_idx in top_term_indices:
                if term_idx < len(feature_names):
                    weight = centroids[cid][term_idx]
                    if weight > 0.0:
                        dominant_terms.append(feature_names[term_idx])

            if not dominant_terms:
                dominant_terms = ["technology", "method", "system"]

            # Dominant Technology Domain
            domains = [p.technology_domain for p, _ in members_with_dist if p.technology_domain]
            dominant_domain = Counter(domains).most_common(1)[0][0] if domains else "Cross-Disciplinary IP"

            # Dominant terms string for naming
            top_terms_label = ", ".join(dominant_terms[:2])
            cluster_name = f"{dominant_domain} — [{top_terms_label}]"

            # Sort members by distance to centroid (most central first)
            members_with_dist.sort(key=lambda x: x[1])

            avg_citations = round(
                sum(p.citation_count for p, _ in members_with_dist) / float(p_count), 2
            )

            rep_members: List[PatentClusterMember] = []
            for p, dist in members_with_dist:
                dist_rounded = round(dist, 3)
                explanation = (
                    f"Assigned with centroid distance {dist_rounded}; closely aligns with dominant "
                    f"cluster terms ({', '.join(dominant_terms[:3])}) and domain '{dominant_domain}'."
                )
                rep_members.append(
                    PatentClusterMember(
                        patent_id=p.id,
                        patent_number=p.patent_number,
                        title=p.title,
                        assignee=p.assignee,
                        technology_domain=p.technology_domain,
                        patent_classification=p.patent_classification,
                        citation_count=p.citation_count,
                        distance_to_centroid=dist_rounded,
                        explanation=explanation,
                    )
                )

            description = (
                f"Cluster {cid + 1} represents {p_count} patent disclosure(s) ({share_pct}% portfolio share) "
                f"principally concentrated in '{dominant_domain}' with prominent technical features {', '.join(dominant_terms[:4])}."
            )

            cluster_items.append(
                PatentClusterItem(
                    cluster_id=cid + 1,
                    cluster_name=cluster_name,
                    technology_domain=dominant_domain,
                    patent_count=p_count,
                    share_percentage=share_pct,
                    dominant_terms=dominant_terms,
                    average_citations=avg_citations,
                    representative_patents=rep_members,
                    description=description,
                )
            )

        # Sort clusters by size descending
        cluster_items.sort(key=lambda c: c.patent_count, reverse=True)

        # Re-number cluster IDs in sorted order for consistent presentation
        for rank, c_item in enumerate(cluster_items, start=1):
            c_item.cluster_id = rank

        return PatentClusteringResponse(
            total_patents=total_patents,
            total_clusters=len(cluster_items),
            algorithm="TF-IDF Vectorization + K-Means Clustering",
            k_requested=k,
            clusters=cluster_items,
            disclaimer="Unsupervised machine learning clustering based on scikit-learn TF-IDF text representations and K-Means centroid optimization."
        )
