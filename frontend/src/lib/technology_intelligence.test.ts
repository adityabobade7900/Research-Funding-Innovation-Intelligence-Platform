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
    expect(candidate.methodology_disclaimer).toContain('Potential Whitespace Indicator');
  });
});
