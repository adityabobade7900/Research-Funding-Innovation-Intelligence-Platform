export interface TechnologyActivityItem {
  technology_area: string;
  technology_domain: string;
  classification_code?: string | null;
  patent_count: number;
  recent_patent_count: number;
  filing_count: number;
  grant_count: number;
  citation_count: number;
  average_citations: number;
  assignee_count: number;
  jurisdictions: string[];
  activity_level: 'HIGH_ACTIVITY' | 'MEDIUM_ACTIVITY' | 'LOW_ACTIVITY';
}

export interface TechnologyActivityResponse {
  items: TechnologyActivityItem[];
  total_patents: number;
  total_technology_areas: number;
  summary_by_level: Record<string, number>;
  timeframe_analyzed: {
    start_year?: number | null;
    end_year?: number | null;
  };
}

export interface TechnologyGrowthItem {
  technology_area: string;
  technology_domain: string;
  recent_period_filings: number;
  historical_period_filings: number;
  growth_rate_pct?: number | null;
  velocity_score: number;
  cagr_pct?: number | null;
  cagr_status?: string;
  growth_trajectory: 'RAPID_ACCELERATION' | 'STEADY_GROWTH' | 'MATURE_STABLE' | 'DECLINING' | 'EMERGING_SPARSE';
}

export interface TechnologyGrowthResponse {
  items: TechnologyGrowthItem[];
  total_growing_areas: number;
  summary_by_trajectory: Record<string, number>;
  timeframe_analyzed: {
    start_year?: number | null;
    end_year?: number | null;
  };
}

export interface TechnologyCoverageItem {
  technology_area: string;
  technology_domain: string;
  patent_count: number;
  assignee_count: number;
  jurisdiction_count: number;
  classification_count: number;
  coverage_density_score: number;
  coverage_level: 'HIGH_COVERAGE' | 'MODERATE_COVERAGE' | 'SPARSE_COVERAGE';
}

export interface TechnologyCoverageResponse {
  items: TechnologyCoverageItem[];
  total_areas: number;
  summary_by_level: Record<string, number>;
}

export interface WhitespaceCandidateItem {
  technology_area: string;
  technology_domain: string;
  classification_code?: string | null;
  whitespace_type: 'POTENTIAL_WHITESPACE' | 'ACTIVITY_GAP' | 'LOW_COVERAGE_AREA' | 'UNDERREPRESENTED_NICHE';
  whitespace_score: number;
  activity_gap_score: number;
  assignee_gap_score: number;
  growth_gap_score: number;
  coverage_gap_score: number;
  publication_count?: number;
  patent_count?: number;
  research_to_patent_ratio?: number | null;
  patent_status_note?: string | null;
  publication_density_score?: number;
  patent_density_score?: number;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence: string[];
  adjacent_technology_areas: string[];
  methodology_disclaimer: string;
}

export interface WhitespaceDiscoveryResponse {
  candidates: WhitespaceCandidateItem[];
  total_candidates: number;
  domain_filter?: string | null;
  threshold_used: number;
  methodology_disclaimer: string;
}

export interface MaturityIndicatorBreakdown {
  research_growth_score: number;
  patent_growth_score: number;
  research_activity_score: number;
  patent_activity_score: number;
  organization_participation_score: number;
  technology_diversity_score: number;
  research_cagr?: number | null;
  patent_cagr?: number | null;
  growth_status?: string;
  weights: Record<string, number>;
}

export interface TechnologyMaturityItem {
  technology_domain: string;
  maturity_score: number;
  stage: 'EMERGING' | 'DEVELOPING' | 'MATURE' | 'DECLINING' | 'INSUFFICIENT_DATA';
  publication_count: number;
  patent_count: number;
  recent_publication_count: number;
  recent_patent_count: number;
  assignee_count: number;
  venue_count: number;
  indicators: MaturityIndicatorBreakdown;
  explainability_summary: string;
  evidence: string[];
}

export interface TechnologyMaturityResponse {
  items: TechnologyMaturityItem[];
  total_domains_analyzed: number;
  summary_by_stage: Record<string, number>;
  weighting_schema: Record<string, number>;
  methodology_notes: string;
}

export interface AdoptionTrackingItem {
  technology_domain: string;
  adoption_status: string;
  adoption_score?: number | null;
  commercial_evidence_available: boolean;
  research_activity_level: string;
  patent_activity_level: string;
  disclaimer: string;
  notes: string;
}

export interface AdoptionTrackingResponse {
  items: AdoptionTrackingItem[];
  total_domains: number;
  disclaimer: string;
}

export interface EmergingTechnologyItem {
  technology_domain: string;
  emerging_score: number;
  growth_trajectory: string;
  research_growth_pct?: number | null;
  patent_velocity_score: number;
  publication_count: number;
  patent_count: number;
  organization_count: number;
  key_signals: string[];
  rationale: string;
}

export interface EmergingTechnologyResponse {
  candidates: EmergingTechnologyItem[];
  total_candidates: number;
}

export interface CompetitiveTechnologyItem {
  technology_domain: string;
  assignee_count: number;
  top_assignees: Array<{
    assignee: string;
    patent_count: number;
    share_pct: number;
    citations?: number;
  }>;
  assignee_concentration_hhi: number;
  concentration_tier: 'UNCONCENTRATED' | 'MODERATELY_CONCENTRATED' | 'HIGHLY_CONCENTRATED';
  composite_competitive_index: number;
  dominant_jurisdictions: string[];
}

export interface CompetitiveTechnologyResponse {
  items: CompetitiveTechnologyItem[];
  total_domains: number;
}

export interface TechnologyIntelligenceSummary {
  total_patents: number;
  total_technology_areas: number;
  active_areas_count: number;
  growing_areas_count: number;
  potential_whitespaces_count: number;
  top_active_areas: TechnologyActivityItem[];
  top_growing_areas: TechnologyGrowthItem[];
  top_whitespace_candidates: WhitespaceCandidateItem[];
  top_maturing_areas?: TechnologyMaturityItem[];
  top_emerging_candidates?: EmergingTechnologyItem[];
  methodology_disclaimer: string;
}
