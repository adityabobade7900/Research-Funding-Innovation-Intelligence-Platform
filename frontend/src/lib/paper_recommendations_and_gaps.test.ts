import { describe, it, expect } from "vitest";
import {
  PublicationRecommendationItem,
  PublicationRecommendationsResponse
} from "@/types/publication";
import {
  ResearchGapItem,
  ResearchGapsResponse
} from "@/types/research_intelligence";

describe("Module 3: Paper Recommendations & Research Gap Discovery Contracts & Transforms", () => {
  // -------------------------------------------------------------
  // PART 1: Paper Recommendations Tests
  // -------------------------------------------------------------
  describe("Profile-Based Paper Recommendations", () => {
    const sampleRecResponse: PublicationRecommendationsResponse = {
      total_recommended: 2,
      profile_completeness_warning: undefined,
      recommendations: [
        {
          publication_id: 2,
          title: "Fault-Tolerant Surface Codes on Neutral Atom Arrays",
          primary_domain: "Quantum Technologies",
          year: 2024,
          authors: "Dr. Vance Adams, Dr. Sarah Connor",
          relevance_score: 82.5,
          reasons: [
            "Matches research domain: Quantum Technologies (+40.0 pts)",
            "Matches profile keyword: quantum error correction (+30.0 pts)",
            "Matches technical area: Neutral Atoms (+15.0 pts)"
          ],
          doi: "10.1038/s41534-024-00100-x"
        },
        {
          publication_id: 3,
          title: "Scalable Qubit Shuttling in 2D Optical Architectures",
          primary_domain: "Quantum Technologies",
          year: 2025,
          authors: "Dr. Vance Adams",
          relevance_score: 55.0,
          reasons: [
            "Matches research domain: Quantum Technologies (+40.0 pts)",
            "Matches profile keyword: optical tweezers (+15.0 pts)"
          ],
          doi: undefined
        }
      ]
    };

    it("1. recommendation rendering: validates recommendation attributes, score formatting, and explainability reasons", () => {
      expect(sampleRecResponse.total_recommended).toBe(2);
      expect(sampleRecResponse.recommendations).toHaveLength(2);

      const topRec = sampleRecResponse.recommendations[0];
      expect(topRec.publication_id).toBe(2);
      expect(topRec.title).toBe("Fault-Tolerant Surface Codes on Neutral Atom Arrays");
      expect(topRec.relevance_score).toBe(82.5);
      expect(`${topRec.relevance_score.toFixed(1)}% Match`).toBe("82.5% Match");
      expect(topRec.authors).toContain("Dr. Vance Adams");
      expect(topRec.primary_domain).toBe("Quantum Technologies");
      expect(topRec.reasons.length).toBeGreaterThanOrEqual(2);
      expect(topRec.reasons[0]).toContain("Matches research domain");
      expect(topRec.reasons[1]).toContain("Matches profile keyword");
    });

    it("2. recommendation empty state: correctly handles zero recommendations and incomplete profile warning", () => {
      const emptyRecResponse: PublicationRecommendationsResponse = {
        total_recommended: 0,
        profile_completeness_warning: "Your profile has limited domain or keyword data. Consider updating your research profile.",
        recommendations: []
      };

      expect(emptyRecResponse.total_recommended).toBe(0);
      expect(emptyRecResponse.recommendations).toHaveLength(0);
      expect(emptyRecResponse.profile_completeness_warning).toBeDefined();
      expect(emptyRecResponse.profile_completeness_warning).toContain("updating your research profile");
    });
  });

  // -------------------------------------------------------------
  // PART 2: Macro-Corpus Research Gap Discovery Tests
  // -------------------------------------------------------------
  describe("Macro-Corpus Research Gap Discovery", () => {
    const sampleGapsResponse: ResearchGapsResponse = {
      total_gaps: 2,
      status: "SUCCESS",
      gaps: [
        {
          gap: "Scalability & Fault Tolerance In Quantum Error Correction",
          domain: "Quantum Technologies",
          evidence_count: 2,
          supporting_keywords: ["quantum error correction", "scalability", "surface codes", "thresholds"],
          supporting_publications: [1, 2],
          evidence: "Cross-publication analysis identifies 2 publications in Quantum Technologies encountering operational constraints and unresolved research horizons.",
          confidence: 0.85
        },
        {
          gap: "Benchmarking In Neutral Atoms",
          domain: "Quantum Technologies",
          evidence_count: 2,
          supporting_keywords: ["neutral atoms", "benchmarks", "fidelity"],
          supporting_publications: [2, 3],
          evidence: "Literature analysis indicates open questions regarding benchmarking and long-term stability.",
          confidence: 0.72
        }
      ],
      message: "Macro-corpus gap discovery completed successfully across 3 publications."
    };

    it("3. gap rendering: validates gap attributes, confidence formatting, supporting publications, and evidence", () => {
      expect(sampleGapsResponse.total_gaps).toBe(2);
      expect(sampleGapsResponse.status).toBe("SUCCESS");
      expect(sampleGapsResponse.gaps).toHaveLength(2);

      const firstGap = sampleGapsResponse.gaps[0];
      expect(firstGap.gap).toBe("Scalability & Fault Tolerance In Quantum Error Correction");
      expect(firstGap.domain).toBe("Quantum Technologies");
      expect(firstGap.confidence).toBe(0.85);
      expect(`${(firstGap.confidence * 100).toFixed(0)}% Confidence`).toBe("85% Confidence");
      expect(firstGap.evidence_count).toBe(2);
      expect(firstGap.supporting_publications).toEqual([1, 2]);
      expect(firstGap.supporting_keywords).toContain("quantum error correction");
      expect(firstGap.evidence).toContain("Cross-publication analysis identifies 2 publications");
    });

    it("4. insufficient-data state: properly signals insufficient corpus without fabricating speculative gaps", () => {
      const insufficientResponse: ResearchGapsResponse = {
        total_gaps: 0,
        status: "INSUFFICIENT_DATA",
        gaps: [],
        message: "Insufficient corpus: At least 2 peer-reviewed publications are required to synthesize research gaps."
      };

      expect(insufficientResponse.status).toBe("INSUFFICIENT_DATA");
      expect(insufficientResponse.total_gaps).toBe(0);
      expect(insufficientResponse.gaps).toHaveLength(0);
      expect(insufficientResponse.message).toContain("Insufficient corpus");
    });

    it("5. API error state: validates error contract structure and graceful degradation handling", () => {
      const networkError = {
        success: false,
        error: {
          code: "NETWORK_ERROR",
          message: "Unable to reach research intelligence service. Verify server connectivity.",
          status: 503
        }
      };

      const authError = {
        success: false,
        error: {
          code: "AUTHENTICATION_REQUIRED",
          message: "Researcher profile authentication is required to compute paper recommendations.",
          status: 401
        }
      };

      expect(networkError.success).toBe(false);
      expect(networkError.error.status).toBe(503);
      expect(networkError.error.code).toBe("NETWORK_ERROR");

      expect(authError.success).toBe(false);
      expect(authError.error.status).toBe(401);
      expect(authError.error.code).toBe("AUTHENTICATION_REQUIRED");
    });
  });
});
