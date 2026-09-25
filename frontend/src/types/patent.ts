export interface Patent {
  id: number;
  patent_number: string;
  title: string;
  abstract: string | null;
  assignee: string | null;
  inventors: string | null;
  filing_date: string | null;
  publication_date: string | null;
  patent_classification: string | null;
  technology_domain: string | null;
  citation_count: number;
  source: string;
  external_id: string | null;
  url: string | null;
  is_bookmarked?: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatentCreatePayload {
  patent_number: string;
  title: string;
  abstract?: string;
  assignee?: string;
  inventors?: string;
  filing_date?: string;
  publication_date?: string;
  patent_classification?: string;
  technology_domain?: string;
  citation_count?: number;
  source?: string;
  external_id?: string;
  url?: string;
}

export interface PatentIngestPayload {
  patent_number: string;
  provider?: string;
}

export interface PatentListResponse {
  items: Patent[];
  total: number;
  limit: number;
  offset: number;
}
