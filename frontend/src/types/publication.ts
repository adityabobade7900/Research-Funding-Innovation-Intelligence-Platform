export interface PublicationKeyword {
  id: number;
  publication_id: number;
  keyword: string;
}

export interface Publication {
  id: number;
  title: string;
  authors: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  doi?: string;
  citation_count: number;
  primary_domain?: string;
  source: string;
  external_id?: string;
  url?: string;
  created_at: string;
  updated_at: string;
  keywords: PublicationKeyword[];
}

export interface PublicationCreate {
  title: string;
  authors: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  doi?: string;
  citation_count?: number;
  primary_domain?: string;
  source?: string;
  external_id?: string;
  url?: string;
  keywords?: string[];
  is_primary_author?: boolean;
}

export interface PublicationUpdate {
  title?: string;
  authors?: string;
  abstract?: string;
  publication_date?: string;
  venue?: string;
  doi?: string;
  citation_count?: number;
  primary_domain?: string;
  source?: string;
  external_id?: string;
  url?: string;
  keywords?: string[];
}

export interface PublicationListResponse {
  items: Publication[];
  total: number;
  limit: number;
  offset: number;
}

export interface PaperAnalysisResponse {
  publication_id: number;
  title: string;
  doi?: string;
  primary_domain?: string;
  authors?: string;
  problem_statement: string;
  methodology: string;
  findings_contributions: string;
  limitations: string;
  future_research_directions: string;
  confidence_score: number;
  analysis_source: string;
  analyzed_at: string;
  provider: string;
  key_insights: string[];
}

export interface PublicationRecommendationItem {
  publication_id: number;
  title: string;
  authors: string;
  venue?: string;
  year?: number;
  doi?: string;
  primary_domain?: string;
  citation_count: number;
  relevance_score: number;
  reasons: string[];
}

export interface PublicationRecommendationsResponse {
  total_recommended: number;
  recommendations: PublicationRecommendationItem[];
  profile_completeness_warning?: string;
}


