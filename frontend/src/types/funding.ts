import { ResearchDomain } from './profile';

export interface FundingKeyword {
  id: number;
  funding_opportunity_id: number;
  keyword: string;
}

export interface FundingOpportunity {
  id: number;
  title: string;
  funding_agency: string;
  funding_program: string | null;
  description: string | null;
  funding_amount: number | null;
  currency: string;
  application_deadline: string | null;
  opportunity_type: string | null;
  eligibility_summary: string | null;
  eligible_institutions: string | null;
  geographic_restrictions: string | null;
  status: string;
  source: string;
  external_id: string | null;
  url: string | null;
  created_by_user_id: number | null;
  created_at: string;
  updated_at: string;
  domains: ResearchDomain[];
  keywords: FundingKeyword[];
}

export interface FundingOpportunityCreatePayload {
  title: string;
  funding_agency: string;
  funding_program?: string;
  description?: string;
  funding_amount?: number;
  currency?: string;
  application_deadline?: string;
  opportunity_type?: string;
  eligibility_summary?: string;
  eligible_institutions?: string;
  geographic_restrictions?: string;
  status?: string;
  source?: string;
  external_id?: string;
  url?: string;
  domain_names?: string[];
  keywords?: string[];
}

export interface FundingOpportunityListResponse {
  items: FundingOpportunity[];
  total: number;
  limit: number;
  offset: number;
}

export interface EligibilityEvaluationResult {
  opportunity_id: number;
  opportunity_title: string;
  eligible: boolean;
  eligibility_status: 'ELIGIBLE' | 'INELIGIBLE' | 'INSUFFICIENT_DATA' | 'CONDITIONAL';
  compatibility_score: number;
  matched_criteria: string[];
  failed_criteria: string[];
  warnings: string[];
  missing_information: string[];
  reasons: string[];
}

export interface FundingRecommendationItem {
  opportunity: FundingOpportunity;
  recommendation_score: number;
  eligibility_status: 'ELIGIBLE' | 'CONDITIONAL';
  matched_domains: string[];
  matched_keywords: string[];
  reasons: string[];
  warnings: string[];
}

export interface FundingRecommendationResponse {
  total_recommended: number;
  items: FundingRecommendationItem[];
  profile_summary: {
    user_id: number;
    institution?: string;
    domains: string[];
    keyword_count: number;
    interest_count: number;
  };
  evaluation_timestamp: string;
}

