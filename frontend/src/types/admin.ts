export type UserRole = 'researcher' | 'startup_founder' | 'innovation_manager' | 'administrator';

export interface AdminUserItem {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  institution?: string;
  publications_count: number;
  patents_count: number;
}

export interface AdminUserListResponse {
  items: AdminUserItem[];
  total: number;
  page: number;
  size: number;
  role_counts: Record<string, number>;
}

export interface PipelineTelemetryItem {
  pipeline_name: string;
  category: 'publication' | 'patent' | 'funding';
  provider_name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'OFFLINE';
  latency_ms: number;
  total_ingested_records: number;
  last_sync_timestamp?: string;
  success_rate: number;
  error_rate: number;
}

export interface PipelineTelemetryResponse {
  total_pipelines: number;
  active_pipelines: number;
  degraded_pipelines: number;
  pipelines: PipelineTelemetryItem[];
}

export interface SystemOverviewResponse {
  total_users: number;
  total_publications: number;
  total_patents: number;
  total_funding_opportunities: number;
  total_grant_capital_usd: number;
  total_domains_covered: number;
  database_status: string;
  database_latency_ms: number;
  migration_head: string;
  uptime_seconds: number;
  role_distribution: Record<string, number>;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor_email: string;
  actor_role: string;
  action_category: string;
  action_detail: string;
  target_resource?: string;
  ip_address?: string;
  status: string;
}

export interface AuditLogListResponse {
  items: AuditLogItem[];
  total: number;
}
