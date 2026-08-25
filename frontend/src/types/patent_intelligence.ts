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
