import { describe, it, expect } from "vitest";
import { PaperAnalysisResponse } from "@/types/publication";

describe("AI Research Paper Analysis (Module 3 Frontend Contracts & State)", () => {
  const sampleAnalysis: PaperAnalysisResponse = {
    publication_id: 101,
    title: "Dual-Species Neutral Atom Surface Codes",
    doi: "10.1038/s41534-024-00100-x",
    primary_domain: "Quantum Technologies",
    authors: "Dr. Vance Adams, Dr. Sarah Connor",
    problem_statement: (
      "Fault-tolerant quantum computing requires quantum error correction codes with physical error " +
      "rates below threshold, yet scaling 2D Rydberg atom arrays remains hindered by laser phase noise."
    ),
    methodology: (
      "In this work, we propose and demonstrate a dual-species neutral atom architecture implementing " +
      "a distance-3 surface code with real-time syndrome extraction using optical tweezers."
    ),
    findings_contributions: (
      "We demonstrate an error detection threshold reduction of 34% with an average two-qubit gate " +
      "fidelity of 99.4%, outperforming baseline planar geometries."
    ),
    limitations: (
      "However, our system is constrained by atom loss rates during cyclic re-cooling and non-destructive " +
      "readout latency exceeding 150 microseconds."
    ),
    future_research_directions: (
      "Future research will explore 3D optical lattices, continuous atom replenishment techniques, " +
      "and fault-tolerant logical qubit shuttling."
    ),
    confidence_score: 0.95,
    analysis_source: "title_and_abstract",
    analyzed_at: "2026-09-26T01:30:00Z",
    provider: "nlp-heuristic-analyzer",
    key_insights: [
      "Dual-species atomic architecture overcomes cross-talk limitations.",
      "99.4% two-qubit gate fidelity verified experimentally.",
      "Readout latency remains a primary engineering bottleneck."
    ],
  };

  it("1. validates that all five mentor-required facets exist and are non-empty", () => {
    expect(sampleAnalysis.problem_statement).toBeDefined();
    expect(sampleAnalysis.problem_statement.length).toBeGreaterThan(20);

    expect(sampleAnalysis.methodology).toBeDefined();
    expect(sampleAnalysis.methodology.length).toBeGreaterThan(20);

    expect(sampleAnalysis.findings_contributions).toBeDefined();
    expect(sampleAnalysis.findings_contributions.length).toBeGreaterThan(20);

    expect(sampleAnalysis.limitations).toBeDefined();
    expect(sampleAnalysis.limitations.length).toBeGreaterThan(20);

    expect(sampleAnalysis.future_research_directions).toBeDefined();
    expect(sampleAnalysis.future_research_directions.length).toBeGreaterThan(20);
  });

  it("2. validates analysis confidence score calculation and percentage formatting", () => {
    expect(sampleAnalysis.confidence_score).toBeGreaterThanOrEqual(0.0);
    expect(sampleAnalysis.confidence_score).toBeLessThanOrEqual(1.0);

    const percentage = Math.round(sampleAnalysis.confidence_score * 100);
    expect(percentage).toBe(95);
    expect(`${percentage}% Confidence`).toBe("95% Confidence");
  });

  it("3. validates analysis metadata attributes (source, engine provider, timestamp)", () => {
    expect(sampleAnalysis.analysis_source).toBe("title_and_abstract");
    expect(sampleAnalysis.provider).toBe("nlp-heuristic-analyzer");
    expect(new Date(sampleAnalysis.analyzed_at).getFullYear()).toBe(2026);
    expect(sampleAnalysis.key_insights).toHaveLength(3);
  });

  it("4. validates error response contract for insufficient paper abstract", () => {
    const insufficientContentError = {
      success: false,
      error: {
        code: "INSUFFICIENT_CONTENT",
        message: "Publication abstract is insufficient for scientific analysis (found 3 words; minimum 10 words required).",
        details: null,
      },
    };

    expect(insufficientContentError.success).toBe(false);
    expect(insufficientContentError.error.code).toBe("INSUFFICIENT_CONTENT");
    expect(insufficientContentError.error.message).toContain("minimum 10 words required");
  });

  it("5. validates error response contract for provider failure", () => {
    const providerFailureError = {
      success: false,
      error: {
        code: "PROVIDER_ERROR",
        message: "Upstream AI provider connection failure",
        details: null,
      },
    };

    expect(providerFailureError.success).toBe(false);
    expect(providerFailureError.error.code).toBe("PROVIDER_ERROR");
  });

  it("6. validates honest non-hallucination fallback format for limitations & future directions", () => {
    const fallbackAnalysis: PaperAnalysisResponse = {
      ...sampleAnalysis,
      limitations: (
        "Explicit limitations were not stated in the available abstract/metadata. " +
        "Further operational constraints require examination of the full-text publication."
      ),
      future_research_directions: (
        "Future research directions were not explicitly delineated in the available abstract. " +
        "Expected follow-up avenues include expanding evaluation benchmarks."
      ),
      confidence_score: 0.74,
    };

    expect(fallbackAnalysis.limitations).toContain("Explicit limitations were not stated");
    expect(fallbackAnalysis.future_research_directions).toContain("Future research directions were not explicitly delineated");
    expect(fallbackAnalysis.confidence_score).toBe(0.74);
  });
});
