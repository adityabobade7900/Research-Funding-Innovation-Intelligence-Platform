from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.profile import Profile
from app.schemas.common import ApiResponse
from app.schemas.commercialization import (
    CommercializationResponse,
    CommercializationReadinessItem,
    CommercializationSummary,
)
from app.services.commercialization_service import CommercializationService

router = APIRouter()


async def _resolve_profile_id(
    my_profile_only: bool,
    current_user: Optional[User],
    db: AsyncSession
) -> Optional[int]:
    """Helper to resolve profile_id if my_profile_only is requested and user is authenticated."""
    if not my_profile_only or not current_user:
        return None

    stmt = select(Profile.id).where(Profile.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@router.get(
    "/recommendations",
    response_model=ApiResponse[CommercializationResponse],
    status_code=status.HTTP_200_OK,
    summary="Commercialization Intelligence & Recommendations",
    description="Computes Commercialization Readiness (0-100) and synthesizes prioritized, explainable commercialization pathways (Startup, Licensing, Industry Collaboration, Grant Funding, IP Strengthening, Validation)."
)
async def get_commercialization_recommendations(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await CommercializationService.evaluate_commercialization(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=result,
        message=f"Generated commercialization recommendations for {result.target_name} (Primary: {result.readiness.primary_pathway})"
    )


@router.get(
    "/readiness",
    response_model=ApiResponse[CommercializationReadinessItem],
    status_code=status.HTTP_200_OK,
    summary="Commercialization Readiness Score",
    description="Evaluates 5-dimensional Commercialization Readiness score (TRL 30%, Patent Strength 25%, Market Potential 20%, Funding Relevance 15%, Novelty 10%)."
)
async def get_commercialization_readiness(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await CommercializationService.evaluate_commercialization(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=result.readiness,
        message=f"Calculated commercialization readiness: {result.readiness.readiness_score}/100 ({result.readiness.readiness_level})"
    )


@router.get(
    "/summary",
    response_model=ApiResponse[CommercializationSummary],
    status_code=status.HTTP_200_OK,
    summary="Commercialization Portfolio Summary",
    description="Cross-domain summary of average readiness scores, pathway distributions, and top commercialization prospects."
)
async def get_commercialization_summary(
    db: AsyncSession = Depends(get_db),
):
    result = await CommercializationService.get_summary(db=db)
    return ApiResponse(
        data=result,
        message="Retrieved commercialization portfolio summary"
    )


@router.get(
    "/evidence",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Commercialization Evidence Breakdown",
    description="Provides detailed explainable rationales and empirical evidence for all generated commercialization recommendations."
)
async def get_commercialization_evidence(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await CommercializationService.evaluate_commercialization(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    evidence_payload = {
        "target_name": result.target_name,
        "readiness_score": result.readiness.readiness_score,
        "readiness_level": result.readiness.readiness_level,
        "primary_pathway": result.readiness.primary_pathway,
        "recommendations": [
            {
                "recommendation_type": r.recommendation_type,
                "title": r.title,
                "priority": r.priority,
                "score": r.score,
                "confidence": r.confidence,
                "rationale": r.rationale,
                "supporting_evidence": r.supporting_evidence,
                "required_next_actions": r.required_next_actions,
            }
            for r in result.recommendations
        ],
        "commercialization_analysis": result.commercialization_analysis.model_dump() if result.commercialization_analysis else None,
        "pathways": result.pathways.model_dump() if result.pathways else None,
        "funding_opportunities_matched": len(result.funding_opportunities),
        "whitespace_context": result.whitespace_context,
        "governance_disclaimer": result.governance_disclaimer,
    }
    return ApiResponse(
        data=evidence_payload,
        message="Retrieved commercialization evidence breakdown"
    )
