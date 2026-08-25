import { describe, it, expect } from 'vitest';
import {
  CommercializationReadinessItem,
  CommercializationRecommendationItem,
  CommercializationResponse,
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
      data_sufficiency: 'SUFFICIENT',
      primary_pathway: 'STARTUP_SPINOUT',
    };

    expect(readiness.readiness_score).toBeGreaterThanOrEqual(0.0);
    expect(readiness.readiness_score).toBeLessThanOrEqual(100.0);
    expect(readiness.readiness_level).toBe('HIGH_COMMERCIAL_READINESS');
    expect(readiness.primary_pathway).toBe('STARTUP_SPINOUT');

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
    expect(recItem.supporting_evidence.length).toBe(2);
    expect(recItem.required_next_actions.length).toBe(2);
  });

  it('validates governance disclaimer in commercialization response', () => {
    const response: Partial<CommercializationResponse> = {
      target_name: 'Quantum Computing',
      target_type: 'DOMAIN',
      governance_disclaimer:
        'Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice.',
    };

    expect(response.governance_disclaimer).toContain('Commercialization recommendations and readiness scores are empirical advisory guidelines');
    expect(response.target_type).toBe('DOMAIN');
  });
});
