import { describe, it, expect } from 'vitest';
import {
  CommercializationReadinessItem,
  CommercializationRecommendationItem,
  CommercializationResponse,
  CommercializationPathwaysContainer,
  CommercializationAnalysisItem,
} from '@/types/commercialization';

describe('Commercialization Intelligence & Recommendations Models', () => {
  it('validates 5-dimensional Commercialization Readiness score bounds', () => {
    const readiness: CommercializationReadinessItem = {
      readiness_score: 75.59,
      readiness_level: 'HIGH_COMMERCIAL_READINESS',
      dimensions: {
        technology_maturity: 77.8,
        patent_strength: 80.0,
        market_potential: 70.0,
        funding_relevance: 65.0,
        research_novelty: 85.0,
      },
      unmeasured_dimensions: {
        regulatory_feasibility: 'DATA_UNAVAILABLE',
        team_capability: 'DATA_UNAVAILABLE',
      },
      data_sufficiency: 'SUFFICIENT',
      primary_pathway: 'STARTUP_CREATION',
    };

    expect(readiness.readiness_score).toBeGreaterThanOrEqual(0.0);
    expect(readiness.readiness_score).toBeLessThanOrEqual(100.0);
    expect(readiness.readiness_level).toBe('HIGH_COMMERCIAL_READINESS');
    expect(readiness.primary_pathway).toBe('STARTUP_CREATION');
    expect(readiness.unmeasured_dimensions?.regulatory_feasibility).toBe('DATA_UNAVAILABLE');
    expect(readiness.unmeasured_dimensions?.team_capability).toBe('DATA_UNAVAILABLE');

    const expectedScore =
      0.30 * readiness.dimensions.technology_maturity +
      0.25 * readiness.dimensions.patent_strength +
      0.20 * readiness.dimensions.market_potential +
      0.15 * readiness.dimensions.funding_relevance +
      0.10 * readiness.dimensions.research_novelty;

    expect(readiness.readiness_score).toBeCloseTo(expectedScore, 1);
  });

  it('validates recommendation items with empirical evidence and action plans', () => {
    const recItem: CommercializationRecommendationItem = {
      recommendation_type: 'LICENSING',
      title: 'Pursue Corporate IP Out-Licensing',
      priority: 'HIGH',
      score: 82.0,
      confidence: 'HIGH',
      data_status: 'AVAILABLE',
      rationale: 'Established patent strength and multi-jurisdiction disclosures enable non-dilutive licensing monetization.',
      supporting_evidence: [
        'Patent Strength: 80.0/100 with granted claims.',
        'Technology Maturity: TRL 6 facilitates tech transfer.',
      ],
      required_next_actions: [
        'Prepare Non-Confidential Technology Summary for corporate IP scouts.',
        'Benchmark royalty rates and standard licensing terms.',
      ],
      limitations: 'Advisory recommendation based on indexed patent and research metadata.',
    };

    expect(recItem.priority).toBe('HIGH');
    expect(recItem.score).toBe(82.0);
    expect(recItem.data_status).toBe('AVAILABLE');
    expect(recItem.supporting_evidence.length).toBe(2);
    expect(recItem.required_next_actions.length).toBe(2);
  });

  it('validates the four canonical commercialization pathways structure', () => {
    const pathways: CommercializationPathwaysContainer = {
      productization: {
        pathway: 'PRODUCTIZATION',
        product_concept: 'Quantum Simulation Platform',
        target_industry: 'Semiconductors, Aerospace',
        problem_addressed: 'Complex multi-qubit circuit simulation bottlenecks.',
        main_use_case: 'Hardware-in-the-loop quantum validation.',
        technology_basis: 'Disclosed quantum circuit patent claims.',
        required_next_steps: ['Develop bill-of-materials model.', 'Establish testbench.'],
        supporting_evidence: ['TRL 5 validation.', 'Patent strength 70/100.'],
        confidence: 'HIGH',
        data_status: 'AVAILABLE',
        score: 68.5,
        limitations: 'Productization concept based on technical disclosures.',
      },
      licensing: {
        pathway: 'LICENSING',
        title: 'Corporate IP Out-Licensing',
        licensing_candidates: [
          {
            organization: 'Quantum Dynamics Corp',
            relevant_domain: 'Quantum Computing',
            evidence_of_relevance: 'Holds 3 related patents.',
            patent_count: 3,
            patent_relationship: 'Corporate Assignee in Domain',
            suggested_licensing_rationale: 'Potential licensing candidate based on domain overlap.',
            confidence: 'HIGH',
            data_status: 'AVAILABLE',
          },
        ],
        ip_ownership_basis: 'Granted patent claims in US and EP.',
        rationale: 'Strong patent defensibility enables corporate out-licensing.',
        supporting_evidence: ['Patent strength 75/100.', '1 corporate candidate identified.'],
        required_next_steps: ['Draft non-confidential pitch.', 'Benchmark royalty rates.'],
        confidence: 'HIGH',
        data_status: 'AVAILABLE',
        score: 72.0,
        limitations: 'Licensing candidates identified strictly via patent overlap.',
      },
      startup_creation: {
        pathway: 'STARTUP_CREATION',
        startup_concept: 'Quantum Acceleration Solutions',
        problem: 'Classical compute limits in material science.',
        proposed_solution: 'Novel quantum co-processor architecture.',
        target_customers: 'Enterprise R&D centers.',
        business_model_hypothesis: 'Tiered enterprise IP licensing.',
        technology_readiness: 'TRL 5',
        relevant_funding: ['DOE Quantum Award ($2.5M)'],
        patent_ip_situation: '2 patents granted.',
        competitive_context: '1 corporate competitor indexed.',
        supporting_evidence: ['Innovation score 72/100.'],
        required_next_steps: ['Engage TTO for license option.', 'Incorporate venture.'],
        confidence: 'HIGH',
        data_status: 'AVAILABLE',
        score: 74.0,
        limitations: 'Does not guarantee venture success.',
      },
      industry_partnership: {
        pathway: 'INDUSTRY_PARTNERSHIP',
        title: 'Industry Co-Development & Joint Validation',
        partnership_candidates: [
          {
            organization: 'Quantum Dynamics Corp',
            partnership_type: 'Technology Validation / Pilot Testing',
            relevant_domain: 'Quantum Computing',
            evidence_of_relevance: 'Active assignee in quantum field.',
            suggested_rationale: 'Potential industry partnership candidate for joint testing.',
            confidence: 'HIGH',
            data_status: 'AVAILABLE',
          },
        ],
        rationale: 'Mid-stage maturity benefits from industrial co-funding.',
        supporting_evidence: ['TRL 5 validation.'],
        required_next_steps: ['Execute Joint Development Agreement.'],
        confidence: 'HIGH',
        data_status: 'AVAILABLE',
        score: 65.0,
        limitations: 'Potential candidate for further evaluation.',
      },
    };

    expect(pathways.productization.pathway).toBe('PRODUCTIZATION');
    expect(pathways.licensing.pathway).toBe('LICENSING');
    expect(pathways.startup_creation.pathway).toBe('STARTUP_CREATION');
    expect(pathways.industry_partnership.pathway).toBe('INDUSTRY_PARTNERSHIP');
    expect(pathways.licensing.licensing_candidates.length).toBe(1);
    expect(pathways.licensing.licensing_candidates[0].organization).toBe('Quantum Dynamics Corp');
  });

  it('validates commercialization analysis with explicit DATA_UNAVAILABLE adoption telemetry', () => {
    const analysis: CommercializationAnalysisItem = {
      research_topic: 'Quantum Computing',
      potential_application_areas: [
        'Hardware-in-the-Loop Quantum Circuit Simulation',
        'Post-Quantum Cryptographic Accelerators',
      ],
      relevant_industries: ['Semiconductors', 'Aerospace & Defense'],
      problem_application_fit: 'Empirical validation indicates suitability for simulation.',
      supporting_evidence: ['TRL 5 validation.', 'Patent strength 70/100.'],
      data_limitations: [
        'Commercial adoption telemetry is DATA_UNAVAILABLE.',
        'Regulatory feasibility is unmeasured.',
      ],
      commercial_adoption_telemetry: 'DATA_UNAVAILABLE',
    };

    expect(analysis.potential_application_areas.length).toBe(2);
    expect(analysis.relevant_industries.length).toBe(2);
    expect(analysis.commercial_adoption_telemetry).toBe('DATA_UNAVAILABLE');
  });

  it('validates governance disclaimer and conservative candidate phrasing', () => {
    const response: Partial<CommercializationResponse> = {
      target_name: 'Quantum Computing',
      target_type: 'DOMAIN',
      governance_disclaimer:
        'Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They represent potential commercialization pathways for further diligence and do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice.',
    };

    expect(response.governance_disclaimer).toContain('potential commercialization pathways for further diligence');
    expect(response.governance_disclaimer).not.toContain('will license');
  });
});
