export interface RoadmapActionItem {
  action: string;
  owner_role: string;
  target_timeline: string;
  expected_outcome: string;
}

export interface RoadmapPhaseItem {
  phase_name: string;
  timeframe: string;
  description: string;
  actions: RoadmapActionItem[];
}

export interface StrategicAssessment {
  strengths: string[];
  risks_and_bottlenecks: string[];
  market_opportunities: string[];
  barriers_to_entry: string[];
}

export interface ExecutiveDossierResponse {
  report_id: string;
  generated_at: string;
  target_name: string;
  target_type: 'PROFILE' | 'DOMAIN';
  executive_summary: string;
  key_findings: string[];
  innovation_score: number;
  innovation_classification: string;
  estimated_trl: number;
  trl_stage: string;
  commercialization_readiness: number;
  readiness_level: string;
  primary_commercial_pathway: string;
  publication_metrics: {
    total_publications: number;
    recent_publications: number;
    total_citations: number;
    average_citations: number;
    venue_count: number;
    novelty_score: number;
  };
  patent_metrics: {
    total_patents: number;
    granted_patents: number;
    jurisdiction_count: number;
    assignee_count: number;
    patent_strength_score: number;
  };
  funding_metrics: {
    matching_opportunities_count: number;
    total_identified_grant_pool: number;
    funding_relevance_score: number;
  };
  whitespace_metrics: {
    detected_whitespace_count: number;
    top_whitespace_areas: string[];
  };
  strategic_assessment: StrategicAssessment;
  roadmap: RoadmapPhaseItem[];
  top_recommendations: Array<{
    recommendation_type: string;
    title: string;
    priority: string;
    score: number;
    confidence: string;
    rationale: string;
    required_next_actions: string[];
  }>;
  top_funding_opportunities: Array<{
    id: number;
    title: string;
    funding_agency: string;
    funding_amount?: number;
    currency?: string;
    application_deadline?: string;
    status?: string;
  }>;
  data_sufficiency: string;
  governance_disclaimer: string;
}

export interface DomainBenchmarkItem {
  domain: string;
  innovation_score: number;
  estimated_trl: number;
  commercialization_readiness: number;
  primary_pathway: string;
  total_publications: number;
  total_patents: number;
  active_funding_streams: number;
}

export interface ExecutiveDossierSummary {
  total_domains_benchmarked: number;
  portfolio_average_innovation_score: number;
  portfolio_average_readiness_score: number;
  dominant_pathway: string;
  trl_breakdown: Record<string, number>;
  domain_benchmarks: DomainBenchmarkItem[];
  governance_disclaimer: string;
}
