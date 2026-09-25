from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.models.user import UserRole


class AdminUserItem(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    institution: Optional[str] = None
    publications_count: int = 0
    patents_count: int = 0


class AdminUserListResponse(BaseModel):
    items: List[AdminUserItem]
    total: int
    page: int
    size: int
    role_counts: Dict[str, int] = Field(default_factory=dict)


class UserRoleUpdateRequest(BaseModel):
    role: UserRole = Field(..., description="New assigned role for the user")


class UserStatusUpdateRequest(BaseModel):
    is_active: bool = Field(..., description="Account activation state")


class PipelineTelemetryItem(BaseModel):
    pipeline_name: str
    category: str  # "publication", "patent", "funding"
    provider_name: str
    status: str  # "HEALTHY", "DEGRADED", "OFFLINE"
    latency_ms: float
    total_ingested_records: int
    last_sync_timestamp: Optional[str] = None
    success_rate: float
    error_rate: float


class PipelineTelemetryResponse(BaseModel):
    total_pipelines: int
    active_pipelines: int
    degraded_pipelines: int
    pipelines: List[PipelineTelemetryItem]


class SystemOverviewResponse(BaseModel):
    total_users: int
    total_publications: int
    total_patents: int
    total_funding_opportunities: int
    total_grant_capital_usd: float
    total_domains_covered: int
    database_status: str
    database_latency_ms: float
    migration_head: str
    uptime_seconds: float
    role_distribution: Dict[str, int] = Field(default_factory=dict)


class AuditLogItem(BaseModel):
    id: str
    timestamp: str
    actor_email: str
    actor_role: str
    action_category: str  # "AUTH", "USER_MGMT", "INGESTION", "RBAC", "INTELLIGENCE"
    action_detail: str
    target_resource: Optional[str] = None
    ip_address: Optional[str] = "127.0.0.1"
    status: str = "SUCCESS"  # "SUCCESS", "FAILED"


class AuditLogListResponse(BaseModel):
    items: List[AuditLogItem]
    total: int
