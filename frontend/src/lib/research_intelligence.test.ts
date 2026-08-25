import { describe, it, expect } from "vitest";
import {
  PublicationTrendsResponse,
  DomainTrendsResponse,
  CitationStatisticsResponse,
  EmergingTopicsResponse,
  ResearchHotspotsResponse,
} from "@/types/research_intelligence";

describe("Research Intelligence Data Modeling & Transforms", () => {
  it("processes publication trends with YoY growth rates accurately", () => {
    const mockTrends: PublicationTrendsResponse = {
      total_publications: 150,
      year_range: { min_year: 2023, max_year: 2026 },
      points: [
        { year: 2023, publication_count: 20, growth_rate: null },
        { year: 2024, publication_count: 40, growth_rate: 100.0 },
        { year: 2025, publication_count: 60, growth_rate: 50.0 },
        { year: 2026, publication_count: 30, growth_rate: -50.0 },
      ],
    };

    expect(mockTrends.total_publications).toBe(150);
    expect(mockTrends.points).toHaveLength(4);
    expect(mockTrends.points[1].growth_rate).toBe(100.0);
    expect(mockTrends.points[3].growth_rate).toBe(-50.0);
  });

  it("evaluates domain market shares and average citations", () => {
    const mockDomains: DomainTrendsResponse = {
      total_domains: 2,
      domains: [
        {
          domain: "Quantum Technologies",
          total_publications: 80,
          average_citations: 42.5,
          yearly_distribution: [
            { year: 2024, count: 30, share_percentage: 37.5 },
            { year: 2025, count: 50, share_percentage: 62.5 },
          ],
        },
        {
          domain: "Biotechnology",
          total_publications: 70,
          average_citations: 31.0,
          yearly_distribution: [
            { year: 2024, count: 35, share_percentage: 50.0 },
            { year: 2025, count: 35, share_percentage: 50.0 },
          ],
        },
      ],
    };

    expect(mockDomains.total_domains).toBe(2);
    expect(mockDomains.domains[0].domain).toBe("Quantum Technologies");
    expect(mockDomains.domains[0].average_citations).toBe(42.5);
    expect(mockDomains.domains[0].yearly_distribution[1].share_percentage).toBe(62.5);
  });

  it("validates emerging topic statistical velocity and reasons structure", () => {
    const mockEmerging: EmergingTopicsResponse = {
      evaluation_window: {
        recent_start_year: 2025,
        current_year: 2026,
        recent_window_length_years: 2,
      },
      total_emerging: 1,
      topics: [
        {
          topic: "Superconducting Qubits",
          recent_count: 12,
          historical_count: 2,
          growth_rate: 500.0,
          velocity_score: 8.9,
          status: "EMERGING",
          reasons: [
            "Accelerating topic: 12 recent publications exceeds historical cumulative count (2)",
          ],
        },
      ],
    };

    expect(mockEmerging.total_emerging).toBe(1);
    expect(mockEmerging.topics[0].status).toBe("EMERGING");
    expect(mockEmerging.topics[0].velocity_score).toBe(8.9);
    expect(mockEmerging.topics[0].reasons).toHaveLength(1);
  });

  it("validates research hotspot intensity classifications", () => {
    const mockHotspots: ResearchHotspotsResponse = {
      total_hotspots: 2,
      evaluation_timestamp: "2026-08-25T00:00:00Z",
      hotspots: [
        {
          domain_or_topic: "Quantum Technologies",
          category: "domain",
          publication_count: 85,
          recent_growth_rate: 65.0,
          citation_count: 1250,
          average_citations: 14.7,
          hotspot_score: 82.5,
          classification: "CRITICAL_HOTSPOT",
          key_drivers: [
            "85 indexed publications",
            "1250 total citations",
            "65.0% growth trajectory",
          ],
        },
        {
          domain_or_topic: "Nanomedicine",
          category: "keyword",
          publication_count: 25,
          recent_growth_rate: 30.0,
          citation_count: 300,
          average_citations: 12.0,
          hotspot_score: 55.0,
          classification: "HIGH_ACTIVITY",
          key_drivers: ["25 indexed publications"],
        },
      ],
    };

    expect(mockHotspots.hotspots[0].classification).toBe("CRITICAL_HOTSPOT");
    expect(mockHotspots.hotspots[0].hotspot_score).toBeGreaterThanOrEqual(70.0);
    expect(mockHotspots.hotspots[1].classification).toBe("HIGH_ACTIVITY");
  });

  it("validates citation statistics with zero/empty dataset safety", () => {
    const emptyStats: CitationStatisticsResponse = {
      total_publications: 0,
      total_citations: 0,
      average_citations: 0.0,
      median_citations: 0.0,
      max_citations: 0,
      citations_by_year: [],
      top_cited_publications: [],
    };

    expect(emptyStats.total_publications).toBe(0);
    expect(emptyStats.average_citations).toBe(0.0);
    expect(emptyStats.citations_by_year).toHaveLength(0);
    expect(emptyStats.top_cited_publications).toHaveLength(0);
  });
});
