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

export interface TechnologyIntelligenceSummary {
  total_patents: number;
  total_technology_areas: number;
  active_areas_count: number;
  growing_areas_count: number;
  potential_whitespaces_count: number;
  top_active_areas: TechnologyActivityItem[];
  top_growing_areas: TechnologyGrowthItem[];
  top_whitespace_candidates: WhitespaceCandidateItem[];
  methodology_disclaimer: string;
}
