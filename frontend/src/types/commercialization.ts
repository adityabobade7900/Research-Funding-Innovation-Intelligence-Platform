export interface ProductizationPathwayItem {
  pathway: 'PRODUCTIZATION';
  product_concept: string;
  target_industry: string;
  problem_addressed: string;
  main_use_case: string;
  technology_basis: string;
  required_next_steps: string[];
  supporting_evidence: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
  score: number;
  limitations: string;
}

export interface LicensingCandidateItem {
  organization: string;
  relevant_domain: string;
  evidence_of_relevance: string;
  patent_count: number;
  patent_relationship: string;
  suggested_licensing_rationale: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
}

export interface LicensingPathwayItem {
  pathway: 'LICENSING';
  title: string;
  licensing_candidates: LicensingCandidateItem[];
  ip_ownership_basis: string;
  rationale: string;
  supporting_evidence: string[];
  required_next_steps: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
  score: number;
  limitations: string;
}

export interface StartupCreationPathwayItem {
  pathway: 'STARTUP_CREATION';
  startup_concept: string;
  problem: string;
  proposed_solution: string;
  target_customers: string;
  business_model_hypothesis: string;
  technology_readiness: string;
  relevant_funding: string[];
  patent_ip_situation: string;
  competitive_context: string;
  supporting_evidence: string[];
  required_next_steps: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
  score: number;
  limitations: string;
}

export interface PartnershipCandidateItem {
  organization: string;
  partnership_type: string;
  relevant_domain: string;
  evidence_of_relevance: string;
  suggested_rationale: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
}

export interface IndustryPartnershipPathwayItem {
  pathway: 'INDUSTRY_PARTNERSHIP';
  title: string;
  partnership_candidates: PartnershipCandidateItem[];
  rationale: string;
  supporting_evidence: string[];
  required_next_steps: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
  score: number;
  limitations: string;
}

export interface CommercializationPathwaysContainer {
  productization: ProductizationPathwayItem;
  licensing: LicensingPathwayItem;
  startup_creation: StartupCreationPathwayItem;
  industry_partnership: IndustryPartnershipPathwayItem;
}

export interface CommercializationAnalysisItem {
  research_topic: string;
  potential_application_areas: string[];
  relevant_industries: string[];
  problem_application_fit: string;
  supporting_evidence: string[];
  data_limitations: string[];
  commercial_adoption_telemetry: string;
}

export interface CommercializationRecommendationItem {
  recommendation_type: string;
  title: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  score: number;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status?: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
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
  unmeasured_dimensions?: Record<string, string>;
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
  commercialization_analysis?: CommercializationAnalysisItem;
  pathways?: CommercializationPathwaysContainer;
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
