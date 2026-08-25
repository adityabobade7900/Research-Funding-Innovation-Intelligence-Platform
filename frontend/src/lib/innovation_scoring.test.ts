import { describe, it, expect } from 'vitest';
import {
  InnovationScoreResponse,
  TRLEstimationItem,
  PillarScoreItem,
} from '@/types/innovation_scoring';

describe('Innovation Scoring & TRL Engine Data Models', () => {
  it('validates 5-pillar weights and score boundaries', () => {
    const noveltyPillar: PillarScoreItem = {
      pillar_name: 'Research Novelty',
      score: 80.0,
      weight: 0.30,
      weighted_score: 24.0,
      is_proxy: true,
      confidence: 'HIGH',
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
      contributing_signals: { estimated_trl: 6, trl_stage: 'System Demonstration' },
      evidence: ['Granted patent disclosures with collaborative assignee participation.'],
      methodology_notes: 'Empirical Technology Maturity Score normalized from 9-stage TRL rule engine.',
    };

    const marketPillar: PillarScoreItem = {
      pillar_name: 'Market Potential',
      score: 70.0,
      weight: 0.20,
      weighted_score: 14.0,
      is_proxy: true,
      confidence: 'MEDIUM',
      contributing_signals: { velocity_score: 75.0, assignee_count: 3 },
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
      target_name: 'Quantum Computing',
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
});
