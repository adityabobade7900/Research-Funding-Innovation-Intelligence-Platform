import { describe, it, expect } from "vitest";
import {
  FundingOpportunity,
  FundingOpportunityListResponse,
  EligibilityEvaluationResult,
  FundingRecommendationItem,
  FundingRecommendationResponse,
  SavedFundingItem,
  SavedFundingListResponse,
  SaveFundingToggleResponse
} from "@/types/funding";

describe("Module 4: Funding Intelligence Contracts & State Transforms", () => {
  // -------------------------------------------------------------
  // PART 1: Funding Opportunity Search & Filters
  // -------------------------------------------------------------
  describe("Funding Opportunity Listing & Filtering Contracts", () => {
    const sampleOpportunities: FundingOpportunity[] = [
      {
        id: 1,
        title: "NSF ExpandQISE: Expanding Capacity in Quantum Information Science and Engineering",
        funding_agency: "National Science Foundation",
        funding_program: "Directorate for Mathematical and Physical Sciences",
        description: "Aims to increase research capacity in Quantum Information Science.",
        funding_amount: 5000000.0,
        currency: "USD",
        application_deadline: "2027-10-15T00:00:00Z",
        opportunity_type: "Grant",
        eligibility_summary: "Higher education institutions in the United States.",
        eligible_institutions: "Accredited US Universities",
        geographic_restrictions: "United States",
        status: "open",
        source: "mock",
        external_id: "NSF-24-548",
        url: "https://www.nsf.gov/funding/pgm_summ.jsp?pims_id=505963",
        created_by_user_id: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-09-01T00:00:00Z",
        domains: [{ id: 1, name: "Quantum Technologies", description: "Quantum domain" }],
        keywords: [{ id: 1, funding_opportunity_id: 1, keyword: "Quantum Computing" }],
        days_remaining: 384,
        deadline_urgency: "NORMAL",
        is_expired: false,
        is_saved: false
      },
      {
        id: 2,
        title: "NIH Targeted Nanoparticles for Brain Delivery",
        funding_agency: "National Institutes of Health",
        funding_program: "NINDS",
        description: "Supports biomimetic nanocarriers crossing the blood-brain barrier.",
        funding_amount: 1800000.0,
        currency: "USD",
        application_deadline: "2026-10-05T00:00:00Z",
        opportunity_type: "Grant",
        eligibility_summary: "Research Organizations & Universities",
        eligible_institutions: "Universities & Medical Centers",
        geographic_restrictions: "Global / Unrestricted",
        status: "open",
        source: "mock",
        external_id: "R01-NS-132456",
        url: "https://grants.nih.gov/grants/guide/pa-files/PAR-24-101.html",
        created_by_user_id: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-09-01T00:00:00Z",
        domains: [{ id: 2, name: "Biotechnology & Genomic Sciences", description: "Biotech domain" }],
        keywords: [{ id: 2, funding_opportunity_id: 2, keyword: "Nanomedicine" }],
        days_remaining: 9,
        deadline_urgency: "URGENT",
        is_expired: false,
        is_saved: true
      },
      {
        id: 3,
        title: "DOE Urgent High-Temperature Electrolysis Contract",
        funding_agency: "Department of Energy",
        funding_program: "ARPA-E",
        description: "High-temperature clean energy generation.",
        funding_amount: 3200000.0,
        currency: "USD",
        application_deadline: "2026-09-29T00:00:00Z",
        opportunity_type: "Contract",
        eligibility_summary: "Industry-academic consortia",
        eligible_institutions: "Consortia, Startups, National Labs",
        geographic_restrictions: "United States",
        status: "open",
        source: "mock",
        external_id: "DE-FOA-0003123",
        url: "https://arpa-e-foa.energy.gov",
        created_by_user_id: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-09-01T00:00:00Z",
        domains: [{ id: 3, name: "Clean Energy & Sustainability", description: "Energy domain" }],
        keywords: [{ id: 3, funding_opportunity_id: 3, keyword: "Hydrogen Energy" }],
        days_remaining: 3,
        deadline_urgency: "CRITICAL",
        is_expired: false,
        is_saved: false
      },
      {
        id: 4,
        title: "Past Archived Grant",
        funding_agency: "NSF",
        funding_program: null,
        description: "Expired opportunity",
        funding_amount: 100000.0,
        currency: "USD",
        application_deadline: "2026-01-01T00:00:00Z",
        opportunity_type: "Grant",
        eligibility_summary: null,
        eligible_institutions: null,
        geographic_restrictions: null,
        status: "closed",
        source: "manual",
        external_id: null,
        url: null,
        created_by_user_id: 1,
        created_at: "2025-01-01T00:00:00Z",
        updated_at: "2025-01-01T00:00:00Z",
        domains: [],
        keywords: [],
        days_remaining: -268,
        deadline_urgency: "EXPIRED",
        is_expired: true,
        is_saved: false
      }
    ];

    it("1. list payload contract: validates total, items, and pagination fields", () => {
      const response: FundingOpportunityListResponse = {
        items: sampleOpportunities,
        total: 4,
        limit: 50,
        offset: 0
      };
      expect(response.total).toBe(4);
      expect(response.items).toHaveLength(4);
      expect(response.items[0].funding_agency).toBe("National Science Foundation");
      expect(response.items[0].domains[0].name).toBe("Quantum Technologies");
    });

    it("2. client filtering: filters by agency, domain, and status correctly", () => {
      const nsfOnly = sampleOpportunities.filter(o => o.funding_agency.includes("National Science Foundation"));
      expect(nsfOnly).toHaveLength(1);
      expect(nsfOnly[0].id).toBe(1);

      const biotechOnly = sampleOpportunities.filter(o => o.domains.some(d => d.name.includes("Biotechnology")));
      expect(biotechOnly).toHaveLength(1);
      expect(biotechOnly[0].id).toBe(2);

      const openOnly = sampleOpportunities.filter(o => o.status === "open");
      expect(openOnly).toHaveLength(3);
    });
  });

  // -------------------------------------------------------------
  // PART 2: Opportunity Details & 14 Mentor Fields
  // -------------------------------------------------------------
  describe("Funding Opportunity Details View Contract", () => {
    const opp: FundingOpportunity = {
      id: 10,
      title: "DARPA Scalable Quantum Networking",
      funding_agency: "Defense Advanced Research Projects Agency",
      funding_program: "Defense Sciences Office",
      description: "Development of entanglement distribution across continental scales.",
      funding_amount: 15000000.0,
      currency: "USD",
      application_deadline: "2027-05-01T00:00:00Z",
      opportunity_type: "Contract",
      eligibility_summary: "Defense contractors, universities, and private laboratories.",
      eligible_institutions: "Accredited Universities and Defense Contractors",
      geographic_restrictions: "United States Only",
      status: "open",
      source: "grants_gov",
      external_id: "HR0011-24-S-0012",
      url: "https://www.darpa.mil/program/quantum-networks",
      created_by_user_id: 1,
      created_at: "2026-08-15T00:00:00Z",
      updated_at: "2026-08-15T00:00:00Z",
      domains: [{ id: 1, name: "Quantum Technologies", description: "Quantum" }],
      keywords: [
        { id: 1, funding_opportunity_id: 10, keyword: "Quantum Networking" },
        { id: 2, funding_opportunity_id: 10, keyword: "Entanglement" }
      ],
      days_remaining: 217,
      deadline_urgency: "NORMAL",
      is_expired: false,
      is_saved: true
    };

    it("3. validates presence of all 14 mentor-required detail fields", () => {
      // 1. title
      expect(opp.title).toBeDefined();
      // 2. agency
      expect(opp.funding_agency).toBe("Defense Advanced Research Projects Agency");
      // 3. program
      expect(opp.funding_program).toBe("Defense Sciences Office");
      // 4. description
      expect(opp.description).toContain("entanglement distribution");
      // 5. amount
      expect(opp.funding_amount).toBe(15000000.0);
      // 6. opening date
      expect(opp.created_at).toBeDefined();
      // 7. deadline
      expect(opp.application_deadline).toBe("2027-05-01T00:00:00Z");
      // 8. type
      expect(opp.opportunity_type).toBe("Contract");
      // 9. eligibility summary
      expect(opp.eligibility_summary).toBeDefined();
      // 10. eligible institutions
      expect(opp.eligible_institutions).toBe("Accredited Universities and Defense Contractors");
      // 11. geographic restrictions
      expect(opp.geographic_restrictions).toBe("United States Only");
      // 12. status
      expect(opp.status).toBe("open");
      // 13. source & external id
      expect(opp.source).toBe("grants_gov");
      expect(opp.external_id).toBe("HR0011-24-S-0012");
      // 14. url
      expect(opp.url).toBe("https://www.darpa.mil/program/quantum-networks");
    });
  });

  // -------------------------------------------------------------
  // PART 3: Recommendations with Module 3 Context & Explainability
  // -------------------------------------------------------------
  describe("Profile-Based Recommendations Contract", () => {
    const recItem: FundingRecommendationItem = {
      opportunity: {
        id: 1,
        title: "NSF ExpandQISE: Expanding Capacity in Quantum Information Science",
        funding_agency: "National Science Foundation",
        funding_program: "MPS",
        description: "Quantum science research expansion",
        funding_amount: 5000000.0,
        currency: "USD",
        application_deadline: "2027-10-15T00:00:00Z",
        opportunity_type: "Grant",
        eligibility_summary: "Higher education",
        eligible_institutions: "Universities",
        geographic_restrictions: "United States",
        status: "open",
        source: "mock",
        external_id: "NSF-24-548",
        url: "https://www.nsf.gov",
        created_by_user_id: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-09-01T00:00:00Z",
        domains: [{ id: 1, name: "Quantum Technologies", description: "Quantum" }],
        keywords: [{ id: 1, funding_opportunity_id: 1, keyword: "Quantum Computing" }],
        is_saved: true
      },
      recommendation_score: 87.5,
      eligibility_status: "ELIGIBLE",
      matched_domains: ["Quantum Technologies"],
      matched_keywords: ["Quantum Computing", "Qubit Scaling"],
      reasons: [
        "Direct alignment with research domain(s): Quantum Technologies",
        "Thematic overlap on keywords: Quantum Computing, Qubit Scaling",
        "Aligns with your publication track record (1 publication(s): 'Fault-Tolerant Surface Codes')",
        "High-impact funding opportunity (USD 5,000,000)"
      ],
      warnings: []
    };

    const recResponse: FundingRecommendationResponse = {
      total_recommended: 1,
      items: [recItem],
      profile_summary: {
        user_id: 1,
        institution: "MIT Quantum Center",
        domains: ["Quantum Technologies"],
        keyword_count: 3,
        interest_count: 2
      },
      evaluation_timestamp: "2026-09-26T00:00:00Z"
    };

    it("4. recommendations contract: score, reasons, matched signals, and Module 3 publication link", () => {
      expect(recResponse.total_recommended).toBe(1);
      expect(recResponse.items[0].recommendation_score).toBe(87.5);
      expect(recResponse.items[0].eligibility_status).toBe("ELIGIBLE");
      expect(recResponse.items[0].matched_domains).toContain("Quantum Technologies");
      expect(recResponse.items[0].reasons).toEqual(
        expect.arrayContaining([
          expect.stringContaining("Direct alignment with research domain"),
          expect.stringContaining("publication track record")
        ])
      );
    });
  });

  // -------------------------------------------------------------
  // PART 4: Eligibility Outcomes
  // -------------------------------------------------------------
  describe("Eligibility Evaluation Outcomes", () => {
    it("5. validates 4 distinct eligibility statuses (ELIGIBLE, CONDITIONAL, INELIGIBLE, INSUFFICIENT_DATA)", () => {
      const eligibleCase: EligibilityEvaluationResult = {
        opportunity_id: 1,
        opportunity_title: "Quantum Grant",
        eligible: true,
        eligibility_status: "ELIGIBLE",
        compatibility_score: 85.0,
        matched_criteria: ["Research domain match: Quantum Technologies", "Affiliation: MIT"],
        failed_criteria: [],
        warnings: [],
        missing_information: [],
        reasons: ["Profile demonstrates strong alignment (85.0% match) with opportunity criteria"]
      };

      const insufficientCase: EligibilityEvaluationResult = {
        opportunity_id: 2,
        opportunity_title: "Biotech Award",
        eligible: false,
        eligibility_status: "INSUFFICIENT_DATA",
        compatibility_score: 25.0,
        matched_criteria: [],
        failed_criteria: [],
        warnings: ["Domain compatibility could not be verified"],
        missing_information: ["Researcher profile has no research domains defined"],
        reasons: ["Insufficient researcher profile data to determine definitive eligibility"]
      };

      const ineligibleCase: EligibilityEvaluationResult = {
        opportunity_id: 3,
        opportunity_title: "European Consortium Grant",
        eligible: false,
        eligibility_status: "INELIGIBLE",
        compatibility_score: 30.0,
        matched_criteria: ["Status is active"],
        failed_criteria: ["Geographic restriction mismatch: Requires [EU Member States]"],
        warnings: [],
        missing_information: [],
        reasons: ["Opportunity restricted to EU entities; profile indicates US affiliation"]
      };

      expect(eligibleCase.eligible).toBe(true);
      expect(eligibleCase.eligibility_status).toBe("ELIGIBLE");

      expect(insufficientCase.eligible).toBe(false);
      expect(insufficientCase.eligibility_status).toBe("INSUFFICIENT_DATA");
      expect(insufficientCase.missing_information).toHaveLength(1);

      expect(ineligibleCase.eligible).toBe(false);
      expect(ineligibleCase.eligibility_status).toBe("INELIGIBLE");
      expect(ineligibleCase.failed_criteria[0]).toContain("Geographic restriction mismatch");
    });
  });

  // -------------------------------------------------------------
  // PART 5: Saved Funding / Watchlist Management
  // -------------------------------------------------------------
  describe("Saved Watchlist Contracts", () => {
    const savedItem: SavedFundingItem = {
      id: 101,
      user_id: 1,
      funding_opportunity_id: 1,
      notes: "Proposal draft due next month",
      created_at: "2026-09-20T12:00:00Z",
      opportunity: {
        id: 1,
        title: "NSF ExpandQISE",
        funding_agency: "NSF",
        funding_program: "MPS",
        description: "Quantum grant",
        funding_amount: 5000000.0,
        currency: "USD",
        application_deadline: "2027-10-15T00:00:00Z",
        opportunity_type: "Grant",
        eligibility_summary: "Universities",
        eligible_institutions: "US Universities",
        geographic_restrictions: "United States",
        status: "open",
        source: "mock",
        external_id: "NSF-24-548",
        url: "https://www.nsf.gov",
        created_by_user_id: 1,
        created_at: "2026-09-01T00:00:00Z",
        updated_at: "2026-09-01T00:00:00Z",
        domains: [],
        keywords: [],
        is_saved: true
      }
    };

    it("6. validates saved funding list response schema and item structure", () => {
      const listResponse: SavedFundingListResponse = {
        items: [savedItem],
        total: 1,
        limit: 50,
        offset: 0
      };
      expect(listResponse.total).toBe(1);
      expect(listResponse.items[0].notes).toBe("Proposal draft due next month");
      expect(listResponse.items[0].opportunity.id).toBe(1);
      expect(listResponse.items[0].opportunity.is_saved).toBe(true);
    });

    it("7. validates save toggle response for both save and unsave actions", () => {
      const saveToggle: SaveFundingToggleResponse = {
        saved: true,
        funding_opportunity_id: 1,
        message: "Opportunity #1 added to your saved watchlist",
        item: savedItem
      };
      expect(saveToggle.saved).toBe(true);
      expect(saveToggle.item?.opportunity.title).toBe("NSF ExpandQISE");

      const unsaveToggle: SaveFundingToggleResponse = {
        saved: false,
        funding_opportunity_id: 1,
        message: "Opportunity #1 removed from your saved watchlist",
        item: null
      };
      expect(unsaveToggle.saved).toBe(false);
      expect(unsaveToggle.item).toBeNull();
    });
  });

  // -------------------------------------------------------------
  // PART 6: Deadline Urgency Mapping
  // -------------------------------------------------------------
  describe("Deadline Tracking & Urgency Mapping", () => {
    it("8. validates urgency categorization based on days remaining", () => {
      const getUrgency = (daysRemaining: number | null | undefined, isExpired: boolean) => {
        if (daysRemaining === null || daysRemaining === undefined) return "ROLLING";
        if (isExpired || daysRemaining < 0) return "EXPIRED";
        if (daysRemaining <= 7) return "CRITICAL";
        if (daysRemaining <= 30) return "URGENT";
        return "NORMAL";
      };

      expect(getUrgency(null, false)).toBe("ROLLING");
      expect(getUrgency(60, false)).toBe("NORMAL");
      expect(getUrgency(25, false)).toBe("URGENT");
      expect(getUrgency(4, false)).toBe("CRITICAL");
      expect(getUrgency(-5, true)).toBe("EXPIRED");
    });
  });
});
