export interface CommercializationRecommendationItem {
  recommendation_type: string;
  title: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  score: number;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  rationale: string;
  supporting_evidence: string[];
  required_next_actions: string[];
  limitations: string;
}

export interface CommercializationReadinessItem {
  readiness_score: number;
  readiness_level: 'HIGH_COMMERCIAL_READINESS' | 'MODERATE_COMMERCIAL_READINESS' | 'EARLY_DEVELOPMENT' | 'BASIC_RESEARCH_STAGE';
  dimensions: {
    technology_maturity: number;
    patent_strength: number;
    market_potential: number;
    funding_relevance: number;
    research_novelty: number;
  };
  data_sufficiency: 'SUFFICIENT' | 'PARTIAL_EVIDENCE' | 'INSUFFICIENT_DATA';
  primary_pathway: string;
}

export interface CommercializationFundingOpportunity {
  id: number;
  title: string;
  funding_agency: string;
  funding_amount?: number;
  currency?: string;
  application_deadline?: string;
  status?: string;
}

export interface CommercializationResponse {
  target_name: string;
  target_type: 'PROFILE' | 'DOMAIN';
  readiness: CommercializationReadinessItem;
  primary_recommendation: CommercializationRecommendationItem;
  recommendations: CommercializationRecommendationItem[];
  innovation_context: {
    innovation_score: number;
    overall_classification: string;
    estimated_trl: number;
    trl_stage: string;
    pillars: Record<string, { score: number; weight: number; weighted_score: number }>;
  };
  funding_opportunities: CommercializationFundingOpportunity[];
  whitespace_context: string[];
  governance_disclaimer: string;
}

export interface DomainCommercializationItem {
  domain: string;
  readiness_score: number;
  readiness_level: string;
  primary_pathway: string;
  estimated_trl: number;
  innovation_score: number;
  recommendation_count: number;
}

export interface CommercializationSummary {
  total_evaluations: number;
  average_readiness_score: number;
  readiness_distribution: Record<string, number>;
  pathway_distribution: Record<string, number>;
  top_commercial_prospects: DomainCommercializationItem[];
  governance_disclaimer: string;
}
