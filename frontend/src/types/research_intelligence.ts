export interface PublicationTrendPoint {
  year: number;
  publication_count: number;
  growth_rate: number | null;
}

export interface PublicationTrendsResponse {
  total_publications: number;
  year_range: {
    min_year: number | null;
    max_year: number | null;
  };
  points: PublicationTrendPoint[];
}

export interface DomainYearPoint {
  year: number;
  count: number;
  share_percentage: number;
}

export interface DomainTrendItem {
  domain: string;
  total_publications: number;
  average_citations: number;
  yearly_distribution: DomainYearPoint[];
}

export interface DomainTrendsResponse {
  total_domains: number;
  domains: DomainTrendItem[];
}

export interface KeywordYearPoint {
  year: number;
  count: number;
}

export interface KeywordTrendItem {
  keyword: string;
  total_occurrences: number;
  recent_count: number;
  yearly_distribution: KeywordYearPoint[];
}

export interface KeywordTrendsResponse {
  total_keywords: number;
  keywords: KeywordTrendItem[];
}

export interface TopCitedPublicationSummary {
  id: number;
  title: string;
  citation_count: number;
  publication_date: string | null;
  venue: string | null;
  primary_domain: string | null;
  doi: string | null;
}

export interface CitationYearPoint {
  year: number;
  total_citations: number;
  average_citations: number;
  publication_count: number;
}

export interface CitationStatisticsResponse {
  total_publications: number;
  total_citations: number;
  average_citations: number;
  median_citations: number;
  max_citations: number;
  citations_by_year: CitationYearPoint[];
  top_cited_publications: TopCitedPublicationSummary[];
}

export interface EmergingTopicItem {
  topic: string;
  recent_count: number;
  historical_count: number;
  growth_rate: number | null;
  velocity_score: number;
  status: 'EMERGING' | 'ESTABLISHED_GROWING' | 'STABLE';
  reasons: string[];
}

export interface EmergingTopicsResponse {
  evaluation_window: {
    recent_start_year: number;
    current_year: number;
    recent_window_length_years: number;
  };
  total_emerging: number;
  topics: EmergingTopicItem[];
}

export interface ResearchHotspotItem {
  domain_or_topic: string;
  category: 'domain' | 'keyword';
  publication_count: number;
  recent_growth_rate: number | null;
  citation_count: number;
  average_citations: number;
  hotspot_score: number;
  classification: 'CRITICAL_HOTSPOT' | 'HIGH_ACTIVITY' | 'MODERATE_ACTIVITY' | 'EMERGING_NICHE';
  key_drivers: string[];
}

export interface ResearchHotspotsResponse {
  total_hotspots: number;
  evaluation_timestamp: string;
  hotspots: ResearchHotspotItem[];
}
