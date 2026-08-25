import { describe, it, expect } from 'vitest';
import {
  PatentLandscapeSummary,
  PatentTrendsResponse,
  TechnologyDomainsResponse,
  CompetitiveLandscapeResponse,
} from '@/types/patent_intelligence';

describe('Patent Intelligence Types and Transforms', () => {
  it('correctly models PatentLandscapeSummary structures', () => {
    const mockSummary: PatentLandscapeSummary = {
      total_patents: 25,
      total_assignees: 12,
      total_domains: 5,
      total_citations: 180,
      average_citations: 7.2,
      filing_year_range: {
        min_year: 2020,
        max_year: 2024,
      },
      top_domains: [
        {
          domain: 'Quantum Computing',
          patent_count: 10,
          share_percentage: 40.0,
          total_citations: 95,
          average_citations: 9.5,
          top_assignees: ['IBM Corporation', 'Google LLC'],
        },
      ],
      top_assignees: [
        {
          assignee: 'IBM Corporation',
          patent_count: 8,
          share_percentage: 32.0,
          total_citations: 70,
          average_citations: 8.75,
          recent_filings_count: 4,
          primary_domains: ['Quantum Computing'],
          jurisdictions: ['US', 'EP'],
        },
      ],
      jurisdiction_distribution: [
        {
          jurisdiction_code: 'US',
          jurisdiction_name: 'United States Patent and Trademark Office (USPTO)',
          patent_count: 18,
          share_percentage: 72.0,
        },
      ],
    };

    expect(mockSummary.total_patents).toBe(25);
    expect(mockSummary.top_domains[0].share_percentage).toBe(40.0);
    expect(mockSummary.jurisdiction_distribution[0].jurisdiction_code).toBe('US');
  });

  it('correctly validates Technology Concentration Levels', () => {
    const response: TechnologyDomainsResponse = {
      total_domains: 3,
      concentration_index_hhi: 3200.0,
      concentration_level: 'HIGHLY_CONCENTRATED',
      domains: [
        {
          domain: 'Biotechnology',
          patent_count: 15,
          share_percentage: 60.0,
          total_citations: 120,
          average_citations: 8.0,
          top_assignees: ['MIT', 'Stanford'],
        },
      ],
    };

    expect(response.concentration_level).toBe('HIGHLY_CONCENTRATED');
    expect(response.concentration_index_hhi).toBeGreaterThan(2500);
  });

  it('correctly models Competitive Landscape Indicators', () => {
    const compResp: CompetitiveLandscapeResponse = {
      total_competitors: 2,
      methodology_disclaimer: 'Structured Patent Landscape Indicator',
      competitors: [
        {
          assignee: 'Google LLC',
          patent_count: 12,
          domain_breadth_count: 3,
          recent_filing_velocity_pct: 66.67,
          average_citations: 15.4,
          competitive_index: 82.5,
          classification: 'DOMINANT_PORTFOLIO',
          primary_domains: ['Artificial Intelligence', 'Quantum Computing'],
          key_drivers: ['Substantial Portfolio (12 patents)', 'High Active Filing Rate (66.67% recent)'],
        },
      ],
    };

    expect(compResp.competitors[0].competitive_index).toBe(82.5);
    expect(compResp.competitors[0].classification).toBe('DOMINANT_PORTFOLIO');
    expect(compResp.competitors[0].key_drivers.length).toBe(2);
  });
});
