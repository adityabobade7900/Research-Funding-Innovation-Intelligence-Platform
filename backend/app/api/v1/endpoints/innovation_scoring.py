from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user_optional
from app.models.user import User
from app.models.profile import Profile
from app.schemas.common import ApiResponse
from app.schemas.innovation_scoring import (
    InnovationScoreResponse,
    TRLEstimationItem,
    InnovationScoringSummary,
)
from app.services.innovation_scoring_service import InnovationScoringService

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
    "/score",
    response_model=ApiResponse[InnovationScoreResponse],
    status_code=status.HTTP_200_OK,
    summary="Compute 5-Pillar Innovation Score",
    description="Calculates normalized 5-pillar Innovation Score (Research Novelty 30%, Patent Strength 20%, Technology Maturity 15%, Market Potential 20%, Funding Relevance 15%)."
)
async def get_innovation_score(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    result = await InnovationScoringService.calculate_innovation_score(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=result,
        message=f"Calculated 5-pillar innovation score for {result.target_name} ({result.overall_classification})"
    )


@router.get(
    "/trl",
    response_model=ApiResponse[TRLEstimationItem],
    status_code=status.HTTP_200_OK,
    summary="Estimate Technology Readiness Level (TRL 1-9)",
    description="Deterministic rule evaluation engine for estimated Technology Readiness Level (1-9), stage category, confidence, and empirical evidence."
)
async def get_trl_estimation(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    score_resp = await InnovationScoringService.calculate_innovation_score(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )
    return ApiResponse(
        data=score_resp.trl,
        message=f"Estimated TRL {score_resp.trl.estimated_trl} ({score_resp.trl.trl_stage}) with {score_resp.trl.confidence} confidence"
    )


@router.get(
    "/summary",
    response_model=ApiResponse[InnovationScoringSummary],
    status_code=status.HTTP_200_OK,
    summary="Innovation Scoring Executive Summary",
    description="Cross-domain portfolio summary of average innovation scores, TRL distribution, and top innovating research fields."
)
async def get_innovation_summary(
    db: AsyncSession = Depends(get_db),
):
    result = await InnovationScoringService.get_summary(db=db)
    return ApiResponse(
        data=result,
        message="Retrieved innovation scoring executive summary"
    )


@router.get(
    "/evidence",
    response_model=ApiResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Detailed Explainable Evidence Breakdown",
    description="Provides transparent, explainable evidence checklists and contributing metrics across all 5 innovation pillars and TRL."
)
async def get_innovation_evidence(
    domain: Optional[str] = Query(None, description="Optional technology domain filter"),
    my_profile_only: bool = Query(False, description="Scope evaluation exclusively to authenticated user's portfolio"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    profile_id = await _resolve_profile_id(my_profile_only, current_user, db)
    score_resp = await InnovationScoringService.calculate_innovation_score(
        domain=domain,
        profile_id=profile_id,
        db=db,
    )

    evidence_breakdown = {
        "target_name": score_resp.target_name,
        "innovation_score": score_resp.innovation_score,
        "overall_classification": score_resp.overall_classification,
        "data_sufficiency": score_resp.data_sufficiency,
        "trl_evidence": {
            "estimated_trl": score_resp.trl.estimated_trl,
            "trl_stage": score_resp.trl.trl_stage,
            "confidence": score_resp.trl.confidence,
            "evidence_points": score_resp.trl.evidence,
        },
        "pillar_evidence": {
            k: {
                "score": v.score,
                "weight": v.weight,
                "confidence": v.confidence,
                "data_status": v.data_status,
                "normalization_method": v.normalization_method,
                "evidence_points": v.evidence,
                "contributing_signals": v.contributing_signals,
            }
            for k, v in score_resp.pillars.items()
        },
        "key_strengths": score_resp.key_strengths,
        "areas_for_growth": score_resp.areas_for_growth,
        "governance_disclaimer": score_resp.governance_disclaimer,
    }

    return ApiResponse(
        data=evidence_breakdown,
        message="Retrieved explainable innovation evidence breakdown"
    )
