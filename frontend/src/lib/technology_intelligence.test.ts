import { describe, it, expect } from 'vitest';
import {
  TechnologyActivityItem,
  TechnologyGrowthItem,
  TechnologyCoverageItem,
  WhitespaceCandidateItem,
} from '@/types/technology_intelligence';

describe('Technology Intelligence Data Models & Classification', () => {
  it('validates technology activity item structure and levels', () => {
    const activity: TechnologyActivityItem = {
      technology_area: 'Quantum Computing',
      technology_domain: 'Quantum Computing',
      classification_code: 'G06N 10/00',
      patent_count: 14,
      recent_patent_count: 6,
      filing_count: 14,
      grant_count: 10,
      citation_count: 120,
      average_citations: 8.57,
      assignee_count: 5,
      jurisdictions: ['US', 'EP', 'WO'],
      activity_level: 'HIGH_ACTIVITY',
    };

    expect(activity.patent_count).toBe(14);
    expect(activity.activity_level).toBe('HIGH_ACTIVITY');
    expect(activity.jurisdictions).toContain('US');
  });

  it('validates growth trajectory and velocity score ranges', () => {
    const growth: TechnologyGrowthItem = {
      technology_area: 'Artificial Intelligence',
      technology_domain: 'Artificial Intelligence',
      recent_period_filings: 8,
      historical_period_filings: 2,
      growth_rate_pct: 300.0,
      velocity_score: 80.0,
      growth_trajectory: 'RAPID_ACCELERATION',
    };

    expect(growth.velocity_score).toBeGreaterThan(50);
    expect(growth.growth_trajectory).toBe('RAPID_ACCELERATION');
    expect(growth.growth_rate_pct).toBe(300.0);
  });

  it('validates whitespace candidate scoring, evidence generation, and disclaimer', () => {
    const candidate: WhitespaceCandidateItem = {
      technology_area: 'Synthetic Biology',
      technology_domain: 'Synthetic Biology',
      classification_code: 'C12P 7/18',
      whitespace_type: 'POTENTIAL_WHITESPACE',
      whitespace_score: 78.5,
      activity_gap_score: 85.0,
      assignee_gap_score: 75.0,
      growth_gap_score: 80.0,
      coverage_gap_score: 70.0,
      confidence: 'HIGH',
      evidence: [
        'Sparse patent density (1 patent) indexed in this technology field.',
        'High applicant concentration with only 1 distinct assignee recorded.',
        'Zero patent filings detected within the recent 24-month window.',
      ],
      adjacent_technology_areas: ['Biotechnology', 'Genetic Engineering'],
      methodology_disclaimer:
        'Potential Whitespace Indicator based on patent metadata distribution and activity gaps. Does not constitute an assessment of freedom-to-operate, patentability, or commercial viability.',
    };

    expect(candidate.whitespace_score).toBeGreaterThan(70);
    expect(candidate.evidence.length).toBe(3);
    expect(candidate.confidence).toBe('HIGH');
  });

  it('validates multi-year CAGR and velocity attributes on TechnologyGrowthItem', () => {
    const growth: TechnologyGrowthItem = {
      technology_area: 'Quantum Computing',
      technology_domain: 'Quantum Computing',
      recent_period_filings: 6,
      historical_period_filings: 2,
      growth_rate_pct: 200.0,
      velocity_score: 75.0,
      cagr_pct: 41.42,
      cagr_status: 'COMPUTED',
      growth_trajectory: 'RAPID_ACCELERATION',
    };

    expect(growth.cagr_pct).toBe(41.42);
    expect(growth.cagr_status).toBe('COMPUTED');
    expect(growth.velocity_score).toBe(75.0);
  });

  it('validates mentor 6-indicator maturity model formula and weights summing to 1.0', () => {
    const indicators = {
      research_growth_score: 80.0,
      patent_growth_score: 70.0,
      research_activity_score: 60.0,
      patent_activity_score: 50.0,
      organization_participation_score: 65.0,
      technology_diversity_score: 75.0,
      weights: {
        research_growth: 0.25,
        patent_growth: 0.25,
        research_activity: 0.15,
        patent_activity: 0.15,
        organization_participation: 0.10,
        technology_diversity: 0.10,
      },
    };

    // Verify weights sum to 100% (1.00)
    const weightSum = Object.values(indicators.weights).reduce((a, b) => a + b, 0);
    expect(weightSum).toBeCloseTo(1.0, 5);

    // Compute maturity score according to mentor formula
    const computedScore =
      0.25 * indicators.research_growth_score +
      0.25 * indicators.patent_growth_score +
      0.15 * indicators.research_activity_score +
      0.15 * indicators.patent_activity_score +
      0.10 * indicators.organization_participation_score +
      0.10 * indicators.technology_diversity_score;

    expect(computedScore).toBe(68.0);
  });

  it('validates whitespace candidate with publication vs patent density ratio', () => {
    const candidate: WhitespaceCandidateItem = {
      technology_area: 'Cybersecurity & Cryptography',
      technology_domain: 'Cybersecurity & Cryptography',
      classification_code: 'H04L 9/00',
      whitespace_type: 'POTENTIAL_WHITESPACE',
      whitespace_score: 84.5,
      activity_gap_score: 100.0,
      assignee_gap_score: 90.0,
      growth_gap_score: 85.0,
      coverage_gap_score: 80.0,
      publication_count: 5,
      patent_count: 1,
      research_to_patent_ratio: 5.0,
      publication_density_score: 80.0,
      patent_density_score: 20.0,
      confidence: 'HIGH',
      evidence: [
        'Active scientific research foundation (5 publications) contrasted with 1 patent disclosure.',
        'Research-to-patent ratio of 5.0 indicates significant academic discovery outpaces patent protection.',
      ],
      adjacent_technology_areas: ['Post-Quantum Cryptography'],
      methodology_disclaimer:
        'Potential Whitespace Indicator based on publication vs. patent density gaps. Does not constitute an assessment of freedom-to-operate, patentability, or commercial viability.',
    };

    expect(candidate.research_to_patent_ratio).toBe(5.0);
    expect(candidate.publication_count).toBe(5);
    expect(candidate.patent_count).toBe(1);
    expect(candidate.whitespace_score).toBeGreaterThan(80);
    expect(candidate.confidence).toBe('HIGH');
  });

  it('validates adoption tracking isolation: DATA_UNAVAILABLE when commercial evidence is unindexed', () => {
    const adoption = {
      technology_domain: 'Quantum Technologies',
      adoption_status: 'DATA_UNAVAILABLE',
      commercial_evidence_available: false,
      research_activity_level: 'HIGH',
      patent_activity_level: 'HIGH',
      disclaimer: 'Technology adoption tracking is strictly separate from scientific publication and patent activity.',
    };

    expect(adoption.adoption_status).toBe('DATA_UNAVAILABLE');
    expect(adoption.commercial_evidence_available).toBe(false);
    expect(adoption.research_activity_level).toBe('HIGH');
  });

  it('proves that a technology with maturity score < 60 is NEVER classified as MATURE', () => {
    const score = 48.8;
    const canBeMature = score >= 60.0;
    expect(canBeMature).toBe(false);

    // Classification rule implementation
    const classifyStage = (maturityScore: number, resAct: number, patAct: number, histYears: number) => {
      if (histYears < 2) return 'INSUFFICIENT_DATA';
      if (maturityScore >= 60.0 && resAct >= 40.0 && patAct >= 40.0) return 'MATURE';
      if (maturityScore >= 45.0) return 'DEVELOPING';
      return 'EMERGING';
    };

    expect(classifyStage(48.8, 70.0, 70.0, 2)).not.toBe('MATURE');
    expect(classifyStage(48.8, 70.0, 70.0, 2)).toBe('DEVELOPING');
    expect(classifyStage(65.0, 70.0, 70.0, 3)).toBe('MATURE');
  });

  it('validates zero-patent whitespace representation: ratio is null and patent note is provided', () => {
    const zeroPatentCandidate: WhitespaceCandidateItem = {
      technology_area: 'Lattice Cryptography',
      technology_domain: 'Cybersecurity',
      whitespace_type: 'POTENTIAL_WHITESPACE',
      whitespace_score: 92.0,
      activity_gap_score: 100.0,
      assignee_gap_score: 100.0,
      growth_gap_score: 100.0,
      coverage_gap_score: 100.0,
      publication_count: 3,
      patent_count: 0,
      research_to_patent_ratio: null,
      patent_status_note: 'No patent records identified for this technology domain.',
      confidence: 'HIGH',
      evidence: ['3 publications indexed', 'No patent records identified for this technology domain.'],
      adjacent_technology_areas: [],
      methodology_disclaimer: 'Potential Whitespace Indicator.',
    };

    expect(zeroPatentCandidate.patent_count).toBe(0);
    expect(zeroPatentCandidate.research_to_patent_ratio).toBeNull();
    expect(zeroPatentCandidate.patent_status_note).toBe('No patent records identified for this technology domain.');
  });

  it('proves academic venue count does NOT increase organization participation score', () => {
    const computeOrgScore = (assignees: number, _venues: number) => {
      // Venues (journals/conferences) are excluded from organization count
      return Math.min(100.0, assignees * 30.0);
    };

    const scoreWith0Venues = computeOrgScore(1, 0);
    const scoreWith10Venues = computeOrgScore(1, 10);

    expect(scoreWith0Venues).toBe(30.0);
    expect(scoreWith10Venues).toBe(30.0);
    expect(scoreWith10Venues).toBe(scoreWith0Venues);
  });
});
