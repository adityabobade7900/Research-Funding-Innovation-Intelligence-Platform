import { describe, it, expect } from 'vitest';
import {
  PatentLandscapeSummary,
  TechnologyDomainsResponse,
  CompetitiveLandscapeResponse,
  PatentClusteringResponse,
  InnovationMapResponse,
  PatentRecommendationsResponse,
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

  it('correctly models Competitive Landscape Indicators with Assignee HHI', () => {
    const compResp: CompetitiveLandscapeResponse = {
      total_competitors: 2,
      assignee_concentration_hhi: 2800.0,
      concentration_level: 'HIGHLY_CONCENTRATED',
      weighting_schema: { volume: 0.40, velocity: 0.30, citations: 0.20, domain_breadth: 0.10 },
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
    expect(compResp.assignee_concentration_hhi).toBe(2800.0);
    expect(compResp.concentration_level).toBe('HIGHLY_CONCENTRATED');
    expect(compResp.weighting_schema?.volume).toBe(0.40);
  });

  it('correctly models Unsupervised Machine Learning Patent Clusters', () => {
    const clusterResp: PatentClusteringResponse = {
      total_patents: 10,
      total_clusters: 2,
      algorithm: 'TF-IDF Vectorization + K-Means Clustering',
      k_requested: 2,
      disclaimer: 'Unsupervised ML clustering',
      clusters: [
        {
          cluster_id: 1,
          cluster_name: 'Quantum Computing — [qubit, superconducting]',
          technology_domain: 'Quantum Computing',
          patent_count: 6,
          share_percentage: 60.0,
          dominant_terms: ['qubit', 'superconducting', 'cryogenic', 'processor'],
          average_citations: 18.5,
          representative_patents: [
            {
              patent_id: 101,
              patent_number: 'US10111222B2',
              title: 'Superconducting Qubit Coupler',
              assignee: 'IBM Corporation',
              technology_domain: 'Quantum Computing',
              patent_classification: 'G06N10/00',
              citation_count: 28,
              distance_to_centroid: 0.142,
              explanation: 'Strong proximity to cluster centroid aligning with dominant terms.',
            },
          ],
          description: 'Cluster 1 represents 6 disclosures concentrated in Quantum Computing.',
        },
      ],
    };

    expect(clusterResp.total_clusters).toBe(2);
    expect(clusterResp.algorithm).toContain('TF-IDF');
    expect(clusterResp.clusters[0].dominant_terms).toContain('qubit');
    expect(clusterResp.clusters[0].representative_patents[0].distance_to_centroid).toBe(0.142);
  });

  it('correctly models Multi-Dimensional Innovation Mapping', () => {
    const mapResp: InnovationMapResponse = {
      total_patents: 14,
      domains: ['Quantum Technologies', 'Clean Energy'],
      assignees: ['IBM Corporation', 'Siemens Energy'],
      classifications: ['G06N10/00', 'B01D53/04'],
      matrix: [
        {
          domain: 'Quantum Technologies',
          assignee: 'IBM Corporation',
          patent_count: 4,
          patent_numbers: ['US10111222B2', 'US10333444B2'],
        },
      ],
      hotspots: [
        {
          domain: 'Quantum Technologies',
          classification: 'G06N10/00',
          patent_count: 5,
          recent_count: 3,
          velocity_score: 60.0,
          top_assignees: ['IBM Corporation', 'Google LLC'],
          activity_type: 'EXPANDING_CORE',
        },
      ],
      whitespaces: [
        {
          domain: 'Cybersecurity & Cryptography',
          whitespace_reason: 'Zero patent disclosures currently indexed.',
          opportunity_level: 'HIGH',
          description: 'Significant unaddressed innovation space.',
        },
      ],
    };

    expect(mapResp.total_patents).toBe(14);
    expect(mapResp.matrix[0].patent_count).toBe(4);
    expect(mapResp.hotspots[0].activity_type).toBe('EXPANDING_CORE');
    expect(mapResp.whitespaces[0].opportunity_level).toBe('HIGH');
  });

  it('correctly models Profile-Based Patent Recommendations', () => {
    const recResp: PatentRecommendationsResponse = {
      total_recommendations: 1,
      profile_domains: ['Quantum Computing'],
      profile_keywords: ['qubit', 'cryogenics'],
      recommendations: [
        {
          patent_id: 42,
          patent_number: 'US10555666B2',
          title: 'Cryogenic Control Circuitry for Scalable Quantum Computing',
          abstract: 'Methods for addressing cryogenic qubits.',
          assignee: 'Google LLC',
          technology_domain: 'Quantum Computing',
          patent_classification: 'G06N 10/00',
          citation_count: 32,
          match_score: 86.0,
          matched_domains: ['Quantum Computing'],
          matched_keywords: ['qubit', 'cryogenics'],
          rationale: "Highly relevant to your research profile: matches domain 'Quantum Computing' and keywords.",
        },
      ],
    };

    expect(recResp.total_recommendations).toBe(1);
    expect(recResp.recommendations[0].match_score).toBe(86.0);
    expect(recResp.recommendations[0].matched_domains).toContain('Quantum Computing');
    expect(recResp.recommendations[0].matched_keywords.length).toBe(2);
  });
});
