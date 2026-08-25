from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.user import UserRole


class ActivityFeedItem(BaseModel):
    id: str
    timestamp: str
    activity_type: str  # "PUBLICATION", "PATENT", "FUNDING", "SCORING", "DOSSIER"
    title: str
    description: str
    domain: Optional[str] = None
    badge_label: Optional[str] = None
    action_href: str


class RoleContextualMetrics(BaseModel):
    role: UserRole
    role_headline: str
    primary_metric_label: str
    primary_metric_value: str
    secondary_metric_label: str
    secondary_metric_value: str
    tertiary_metric_label: str
    tertiary_metric_value: str
    recommended_focus_action: str
    focus_action_href: str


class CommandCenterOverviewResponse(BaseModel):
    user_name: str
    user_role: UserRole
    is_profile_scoped: bool
    total_publications: int
    total_patents: int
    total_funding_opportunities: int
    total_grant_pool_usd: float
    average_innovation_score: float
    average_readiness_score: float
    dominant_trl_stage: str
    top_recommended_pathway: str
    top_whitespace_areas: List[str] = Field(default_factory=list)
    upcoming_grant_deadlines: List[Dict[str, Any]] = Field(default_factory=list)
    role_metrics: RoleContextualMetrics
    recent_activity: List[ActivityFeedItem] = Field(default_factory=list)


class ActivityFeedResponse(BaseModel):
    items: List[ActivityFeedItem]
    total: int
