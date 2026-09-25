export interface PatentTrendPoint {
  year: number;
  filings_count: number;
  grants_count: number;
  filing_growth_rate: number | null;
}

export interface PatentTrendsResponse {
  total_patents: number;
  year_range: {
    min_year: number | null;
    max_year: number | null;
  };
  points: PatentTrendPoint[];
}

export interface TechnologyDomainItem {
  domain: string;
  patent_count: number;
  share_percentage: number;
  total_citations: number;
  average_citations: number;
  top_assignees: string[];
}

export interface TechnologyDomainsResponse {
  total_domains: number;
  concentration_index_hhi: number;
  concentration_level: 'DIVERSIFIED' | 'MODERATELY_CONCENTRATED' | 'HIGHLY_CONCENTRATED';
  domains: TechnologyDomainItem[];
}

export interface AssigneeLandscapeItem {
  assignee: string;
  patent_count: number;
  share_percentage: number;
  total_citations: number;
  average_citations: number;
  recent_filings_count: number;
  primary_domains: string[];
  jurisdictions: string[];
}

export interface AssigneesResponse {
  total_assignees: number;
  assignee_concentration_hhi?: number;
  concentration_level?: 'DIVERSIFIED' | 'MODERATELY_CONCENTRATED' | 'HIGHLY_CONCENTRATED';
  assignees: AssigneeLandscapeItem[];
}

export interface JurisdictionItem {
  jurisdiction_code: string;
  jurisdiction_name: string;
  patent_count: number;
  share_percentage: number;
}

export interface JurisdictionsResponse {
  total_jurisdictions: number;
  jurisdictions: JurisdictionItem[];
}

export interface PatentStatusItem {
  status: string;
  count: number;
  share_percentage: number;
}

export interface PatentStatusResponse {
  total_patents: number;
  statuses: PatentStatusItem[];
}

export interface CompetitiveAssigneeItem {
  assignee: string;
  patent_count: number;
  domain_breadth_count: number;
  recent_filing_velocity_pct: number;
  average_citations: number;
  competitive_index: number;
  classification: 'DOMINANT_PORTFOLIO' | 'HIGH_VELOCITY' | 'NICHE_SPECIALIST' | 'EMERGING_APPLICANT';
  primary_domains: string[];
  key_drivers: string[];
}

export interface CompetitiveLandscapeResponse {
  total_competitors: number;
  assignee_concentration_hhi?: number;
  concentration_level?: 'DIVERSIFIED' | 'MODERATELY_CONCENTRATED' | 'HIGHLY_CONCENTRATED';
  weighting_schema?: Record<string, number>;
  methodology_disclaimer: string;
  competitors: CompetitiveAssigneeItem[];
}

export interface PatentLandscapeSummary {
  total_patents: number;
  total_assignees: number;
  total_domains: number;
  total_citations: number;
  average_citations: number;
  filing_year_range: {
    min_year: number | null;
    max_year: number | null;
  };
  top_domains: TechnologyDomainItem[];
  top_assignees: AssigneeLandscapeItem[];
  jurisdiction_distribution: JurisdictionItem[];
}

// --- Machine Learning Clustering Types ---
export interface PatentClusterMember {
  patent_id: number;
  patent_number: string;
  title: string;
  assignee: string | null;
  technology_domain: string | null;
  patent_classification: string | null;
  citation_count: number;
  distance_to_centroid: number | null;
  explanation: string;
}

export interface PatentClusterItem {
  cluster_id: number;
  cluster_name: string;
  technology_domain: string;
  patent_count: number;
  share_percentage: number;
  dominant_terms: string[];
  average_citations: number;
  representative_patents: PatentClusterMember[];
  description: string;
}

export interface PatentClusteringResponse {
  total_patents: number;
  total_clusters: number;
  algorithm: string;
  k_requested: number | null;
  clusters: PatentClusterItem[];
  disclaimer: string;
}

// --- Innovation Mapping Types ---
export interface InnovationMapMatrixCell {
  domain: string;
  assignee: string;
  patent_count: number;
  patent_numbers: string[];
}

export interface InnovationMapHotspot {
  domain: string;
  classification: string;
  patent_count: number;
  recent_count: number;
  velocity_score: number;
  top_assignees: string[];
  activity_type: 'EXPANDING_CORE' | 'HIGH_GROWTH' | 'EMERGING';
}

export interface InnovationMapWhitespace {
  domain: string;
  whitespace_reason: string;
  opportunity_level: 'HIGH' | 'MEDIUM' | 'MODERATE';
  description: string;
}

export interface InnovationMapResponse {
  total_patents: number;
  domains: string[];
  assignees: string[];
  classifications: string[];
  matrix: InnovationMapMatrixCell[];
  hotspots: InnovationMapHotspot[];
  whitespaces: InnovationMapWhitespace[];
}

// --- Profile Patent Recommendations Types ---
export interface PatentRecommendationItem {
  patent_id: number;
  patent_number: string;
  title: string;
  abstract: string | null;
  assignee: string | null;
  technology_domain: string | null;
  patent_classification: string | null;
  citation_count: number;
  match_score: number;
  matched_domains: string[];
  matched_keywords: string[];
  rationale: string;
}

export interface PatentRecommendationsResponse {
  total_recommendations: number;
  profile_domains: string[];
  profile_keywords: string[];
  recommendations: PatentRecommendationItem[];
}
