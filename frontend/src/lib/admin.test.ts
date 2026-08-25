import { describe, it, expect } from 'vitest';
import {
  AdminUserItem,
  PipelineTelemetryItem,
  SystemOverviewResponse,
  AuditLogItem,
} from '@/types/admin';

describe('Admin & Governance Console Data Models', () => {
  it('validates AdminUserItem structure and roles', () => {
    const user: AdminUserItem = {
      id: 1,
      email: 'admin@platform.gov',
      full_name: 'Platform Administrator',
      role: 'administrator',
      is_active: true,
      is_superuser: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      institution: 'Global Research Council',
      publications_count: 12,
      patents_count: 5,
    };

    expect(user.role).toBe('administrator');
    expect(user.is_active).toBe(true);
    expect(user.publications_count).toBe(12);
    expect(user.patents_count).toBe(5);
  });

  it('validates PipelineTelemetryItem connectors and health', () => {
    const pipeline: PipelineTelemetryItem = {
      pipeline_name: 'OpenAlex Academic Graph Sync',
      category: 'publication',
      provider_name: 'openalex',
      status: 'HEALTHY',
      latency_ms: 65.4,
      total_ingested_records: 120,
      last_sync_timestamp: new Date().toISOString(),
      success_rate: 99.4,
      error_rate: 0.6,
    };

    expect(pipeline.status).toBe('HEALTHY');
    expect(pipeline.category).toBe('publication');
    expect(pipeline.latency_ms).toBeGreaterThan(0);
    expect(pipeline.success_rate).toBeCloseTo(99.4);
  });

  it('validates SystemOverviewResponse database health and entity counts', () => {
    const overview: SystemOverviewResponse = {
      total_users: 15,
      total_publications: 150,
      total_patents: 85,
      total_funding_opportunities: 40,
      total_grant_capital_usd: 125000000.0,
      total_domains_covered: 8,
      database_status: 'HEALTHY',
      database_latency_ms: 2.4,
      migration_head: 'f8e9f392e6c3',
      uptime_seconds: 86400,
      role_distribution: {
        researcher: 8,
        startup_founder: 4,
        innovation_manager: 2,
        administrator: 1,
      },
    };

    expect(overview.database_status).toBe('HEALTHY');
    expect(overview.migration_head).toBe('f8e9f392e6c3');
    expect(overview.total_users).toBe(15);
    expect(overview.total_grant_capital_usd).toBeGreaterThan(0);
  });

  it('validates AuditLogItem security event records', () => {
    const log: AuditLogItem = {
      id: 'AUDIT-00001',
      timestamp: new Date().toISOString(),
      actor_email: 'admin@platform.gov',
      actor_role: 'administrator',
      action_category: 'RBAC',
      action_detail: 'Updated role for User #5 to innovation_manager',
      target_resource: 'User:5',
      ip_address: '127.0.0.1',
      status: 'SUCCESS',
    };

    expect(log.action_category).toBe('RBAC');
    expect(log.status).toBe('SUCCESS');
  });
});
