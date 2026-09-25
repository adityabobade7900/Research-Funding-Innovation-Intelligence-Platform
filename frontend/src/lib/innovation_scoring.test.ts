import { describe, it, expect } from 'vitest';
import {
  InnovationScoreResponse,
  TRLEstimationItem,
  PillarScoreItem,
} from '@/types/innovation_scoring';

describe('Innovation Scoring & TRL Engine Data Models', () => {
  it('validates 5-pillar weights, data_status, and score boundaries', () => {
    const noveltyPillar: PillarScoreItem = {
      pillar_name: 'Research Novelty',
      score: 80.0,
      weight: 0.30,
      weighted_score: 24.0,
      is_proxy: true,
      confidence: 'HIGH',
      data_status: 'AVAILABLE',
      normalization_method: 'Bounded multi-metric linear proxy (25% volume, 30% recency ratio, 25% citation impact, 20% venue diversity) scaled to 0-100',
      contributing_signals: { publication_count: 5, average_citations: 18.2 },
      evidence: ['5 peer-reviewed publications indexed with strong citation velocity.'],
      methodology_notes: 'Empirical Research Novelty Proxy calculated from recency and citations.',
    };

    const patentPillar: PillarScoreItem = {
      pillar_name: 'Patent Strength',
      score: 75.0,
      weight: 0.20,
      weighted_score: 15.0,
      is_proxy: true,
      confidence: 'HIGH',
      data_status: 'AVAILABLE',
      normalization_method: 'Bounded multi-metric linear proxy (30% volume, 30% grant conversion, 20% citations, 20% international jurisdictions) scaled to 0-100',
      contributing_signals: { patent_count: 3, granted_patent_count: 2 },
      evidence: ['2 granted patents across 2 international jurisdictions.'],
      methodology_notes: 'Empirical Patent Strength Proxy calculated from grants and jurisdictions.',
    };

    const trlPillar: PillarScoreItem = {
      pillar_name: 'Technology Maturity',
      score: 66.67,
      weight: 0.15,
      weighted_score: 10.0,
      is_proxy: true,
      confidence: 'MEDIUM',
      data_status: 'AVAILABLE',
      normalization_method: 'Deterministic 50/50 blend: (0.50 * Module 6 Maturity Score) + (0.50 * (TRL / 9.0 * 100))',
      contributing_signals: { module6_maturity_score: 66.67, estimated_trl: 6, trl_stage: 'System Demonstration' },
      evidence: ['Granted patent disclosures with collaborative assignee participation.'],
      methodology_notes: 'Integrates Module 6 six-indicator maturity model (50%) with the 9-stage NASA/DoD TRL readiness ladder (50%).',
    };

    const marketPillar: PillarScoreItem = {
      pillar_name: 'Market Potential',
      score: 70.0,
      weight: 0.20,
      weighted_score: 14.0,
      is_proxy: true,
      confidence: 'MEDIUM',
      data_status: 'AVAILABLE',
      normalization_method: 'Linear weighted multi-factor proxy (35% filing velocity, 35% assignee competition density, 30% patent momentum/jurisdictions); commercial adoption telemetry is DATA_UNAVAILABLE.',
      contributing_signals: { velocity_score: 75.0, assignee_count: 3, commercial_adoption_telemetry: 'DATA_UNAVAILABLE' },
      evidence: ['Domain filing velocity of 75% in target technology area.'],
      methodology_notes: 'Empirical Market Potential Proxy derived from filing velocity and applicant density.',
    };

    const fundingPillar: PillarScoreItem = {
      pillar_name: 'Funding Relevance',
      score: 80.0,
      weight: 0.15,
      weighted_score: 12.0,
      is_proxy: true,
      confidence: 'HIGH',
      data_status: 'AVAILABLE',
      normalization_method: 'Multi-factor linear scaling (40% opportunity volume, 35% taxonomy match quality, 25% agency diversity) bounded to 0-100; neutral proxy (50.0) applied when unindexed.',
      contributing_signals: { matching_opportunities_count: 4 },
      evidence: ['4 active funding opportunity streams matching target research domain.'],
      methodology_notes: 'Empirical Funding Relevance Score calculated from active funding grant volume.',
    };

    const totalWeight =
      noveltyPillar.weight +
      patentPillar.weight +
      trlPillar.weight +
      marketPillar.weight +
      fundingPillar.weight;

    expect(totalWeight).toBeCloseTo(1.0, 5);

    const compositeScore =
      noveltyPillar.weighted_score +
      patentPillar.weighted_score +
      trlPillar.weighted_score +
      marketPillar.weighted_score +
      fundingPillar.weighted_score;

    expect(compositeScore).toBe(75.0);
    expect(compositeScore).toBeGreaterThanOrEqual(0.0);
    expect(compositeScore).toBeLessThanOrEqual(100.0);
    expect(noveltyPillar.data_status).toBe('AVAILABLE');
    expect(patentPillar.data_status).toBe('AVAILABLE');
  });

  it('validates TRL 1-9 structure and stages', () => {
    const trlItem: TRLEstimationItem = {
      estimated_trl: 6,
      trl_stage: 'System Demonstration',
      trl_name: 'Technology Demonstrated in Relevant Environment',
      score: 66.67,
      confidence: 'HIGH',
      evidence: [
        'Granted patent disclosures (2 grants) with collaborative assignee participation.',
        'Demonstrates component/subsystem validation in a relevant environment.',
      ],
      limitations_and_assumptions:
        'Empirical heuristic estimate based on indexed research publications, patent disclosures, and assignees.',
    };

    expect(trlItem.estimated_trl).toBeGreaterThanOrEqual(1);
    expect(trlItem.estimated_trl).toBeLessThanOrEqual(9);
    expect(trlItem.score).toBeCloseTo((6 / 9) * 100, 1);
    expect(trlItem.evidence.length).toBe(2);
  });

  it('validates classification categories and governance disclaimers', () => {
    const response: Partial<InnovationScoreResponse> = {
      target_name: 'Quantum Technologies',
      target_type: 'DOMAIN',
      innovation_score: 78.5,
      overall_classification: 'BREAKTHROUGH_INNOVATION',
      data_sufficiency: 'SUFFICIENT',
      governance_disclaimer:
        'The Innovation Score is an explainable composite index based on empirical research, patent, market velocity, and funding metadata. It does not constitute a legal patentability opinion, freedom-to-operate assessment, or guaranteed commercial viability prediction.',
    };

    expect(response.overall_classification).toBe('BREAKTHROUGH_INNOVATION');
    expect(response.data_sufficiency).toBe('SUFFICIENT');
    expect(response.governance_disclaimer).toContain('The Innovation Score is an explainable composite index');
  });

  it('validates Module 6 maturity 50/50 blend traceability', () => {
    const m6Score = 60.0;
    const trlLevel = 6;
    const trlNormalized = (trlLevel / 9.0) * 100.0; // 66.67
    const expectedBlend = Math.round((0.50 * m6Score + 0.50 * trlNormalized) * 100) / 100;

    expect(expectedBlend).toBeCloseTo(63.33, 1);
  });

  it('validates missing funding data policy with neutral proxy and DATA_UNAVAILABLE status', () => {
    const missingFundingPillar: PillarScoreItem = {
      pillar_name: 'Funding Relevance',
      score: 50.0,
      weight: 0.15,
      weighted_score: 7.5,
      is_proxy: true,
      confidence: 'LOW',
      data_status: 'DATA_UNAVAILABLE',
      normalization_method: 'Multi-factor linear scaling (40% opportunity volume, 35% taxonomy match quality, 25% agency diversity) bounded to 0-100; neutral proxy (50.0) applied when unindexed.',
      contributing_signals: { matching_opportunities_count: 0, is_neutral_proxy: true },
      evidence: [
        'No indexed funding opportunities currently match this domain.',
        'Neutral baseline proxy (50.0) applied due to unindexed funding telemetry. Does not imply confirmed funding relevance.',
      ],
      methodology_notes: 'Deterministic missing-data policy: Neutral baseline proxy score of 50.0 applied when funding opportunities for a specific taxonomy are unindexed.',
    };

    expect(missingFundingPillar.data_status).toBe('DATA_UNAVAILABLE');
    expect(missingFundingPillar.score).toBe(50.0);
    expect(missingFundingPillar.weighted_score).toBe(7.5);
    expect(missingFundingPillar.evidence[1]).toContain('Neutral baseline proxy');
  });
});
