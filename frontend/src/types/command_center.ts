import { UserRole } from '@/types/admin';

export interface ActivityFeedItem {
  id: string;
  timestamp: string;
  activity_type: string;
  title: string;
  description: string;
  domain?: string;
  badge_label?: string;
  action_href: string;
}

export interface RoleContextualMetrics {
  role: UserRole;
  role_headline: string;
  primary_metric_label: string;
  primary_metric_value: string;
  secondary_metric_label: string;
  secondary_metric_value: string;
  tertiary_metric_label: string;
  tertiary_metric_value: string;
  recommended_focus_action: string;
  focus_action_href: string;
}

export interface UpcomingGrantItem {
  id: number;
  title: string;
  agency: string;
  amount?: number;
  deadline?: string;
}

export interface CommandCenterOverviewResponse {
  user_name: string;
  user_role: UserRole;
  is_profile_scoped: boolean;
  total_publications: number;
  total_patents: number;
  total_funding_opportunities: number;
  total_grant_pool_usd: number;
  average_innovation_score: number;
  average_readiness_score: number;
  dominant_trl_stage: string;
  top_recommended_pathway: string;
  top_whitespace_areas: string[];
  upcoming_grant_deadlines: UpcomingGrantItem[];
  role_metrics: RoleContextualMetrics;
  recent_activity: ActivityFeedItem[];
}
