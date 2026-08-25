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
