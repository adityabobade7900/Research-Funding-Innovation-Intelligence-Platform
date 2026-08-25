import { describe, it, expect } from 'vitest';
import {
  CommandCenterOverviewResponse,
  RoleContextualMetrics,
} from '@/types/command_center';

describe('Command Center & Strategic Command Hub Models', () => {
  it('validates CommandCenterOverviewResponse unified metrics', () => {
    const roleMetrics: RoleContextualMetrics = {
      role: 'startup_founder',
      role_headline: 'Deep-Tech Whitespaces & Venture Spinout Command',
      primary_metric_label: 'Commercial Readiness',
      primary_metric_value: '75.0 / 100',
      secondary_metric_label: 'Tracked Non-Dilutive Capital',
      secondary_metric_value: '$12.5M',
      tertiary_metric_label: 'Primary Pathway',
      tertiary_metric_value: 'STARTUP SPINOUT',
      recommended_focus_action: 'Explore Technology Whitespace Gaps',
      focus_action_href: '/technology-intelligence',
    };

    const overview: CommandCenterOverviewResponse = {
      user_name: 'Alex Founder',
      user_role: 'startup_founder',
      is_profile_scoped: true,
      total_publications: 12,
      total_patents: 4,
      total_funding_opportunities: 8,
      total_grant_pool_usd: 12500000.0,
      average_innovation_score: 82.5,
      average_readiness_score: 75.0,
      dominant_trl_stage: 'TRL 6 (System Demonstration)',
      top_recommended_pathway: 'STARTUP_SPINOUT',
      top_whitespace_areas: ['Topological Transmon Qubits'],
      upcoming_grant_deadlines: [
        {
          id: 101,
          title: 'NSF Quantum Computing Scale-Up',
          agency: 'NSF',
          amount: 5000000,
          deadline: '2026-11-30T00:00:00Z',
        },
      ],
      role_metrics: roleMetrics,
      recent_activity: [
        {
          id: 'ACT-PUB-1',
          timestamp: new Date().toISOString(),
          activity_type: 'PUBLICATION',
          title: 'Fault-Tolerant Quantum Computing',
          description: 'Published in PRX Quantum with 45 citations.',
          badge_label: 'Publication',
          action_href: '/publications',
        },
      ],
    };

    expect(overview.user_role).toBe('startup_founder');
    expect(overview.average_innovation_score).toBe(82.5);
    expect(overview.role_metrics.primary_metric_value).toBe('75.0 / 100');
    expect(overview.upcoming_grant_deadlines.length).toBe(1);
    expect(overview.recent_activity.length).toBe(1);
  });
});
