export interface PillarScoreItem {
  pillar_name: string;
  score: number;
  weight: number;
  weighted_score: number;
  is_proxy: boolean;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  data_status: 'AVAILABLE' | 'INSUFFICIENT_DATA' | 'DATA_UNAVAILABLE';
  normalization_method: string;
  contributing_signals: Record<string, any>;
  evidence: string[];
  methodology_notes: string;
}

export interface TRLEstimationItem {
  estimated_trl: number;
  trl_stage: string;
  trl_name: string;
  score: number;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  evidence: string[];
  limitations_and_assumptions: string;
}

export interface InnovationScoreResponse {
  target_name: string;
  target_type: 'PROFILE' | 'DOMAIN';
  innovation_score: number;
  overall_classification: 'BREAKTHROUGH_INNOVATION' | 'HIGH_POTENTIAL' | 'DEVELOPING_CAPABILITY' | 'EARLY_STAGE_EXPLORATORY';
  data_sufficiency: 'SUFFICIENT' | 'PARTIAL_EVIDENCE' | 'INSUFFICIENT_DATA';
  pillars: {
    research_novelty: PillarScoreItem;
    patent_strength: PillarScoreItem;
    technology_maturity: PillarScoreItem;
    market_potential: PillarScoreItem;
    funding_relevance: PillarScoreItem;
  };
  trl: TRLEstimationItem;
  key_strengths: string[];
  areas_for_growth: string[];
  governance_disclaimer: string;
}

export interface DomainInnovationItem {
  domain: string;
  innovation_score: number;
  estimated_trl: number;
  data_sufficiency: string;
  publication_count: number;
  patent_count: number;
}

export interface InnovationScoringSummary {
  total_evaluations: number;
  average_innovation_score: number;
  trl_distribution: Record<string, number>;
  classification_distribution: Record<string, number>;
  top_innovating_domains: DomainInnovationItem[];
  governance_disclaimer: string;
}
