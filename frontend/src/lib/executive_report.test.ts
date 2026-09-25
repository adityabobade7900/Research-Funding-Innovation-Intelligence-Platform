import { describe, it, expect } from 'vitest';
import {
  ExecutiveDossierResponse,
  StrategicAssessment,
  RoadmapPhaseItem,
} from '@/types/executive_report';

describe('Executive Intelligence Dossier & Reporting Models', () => {
  it('validates comprehensive dossier response synthesis', () => {
    const assessment: StrategicAssessment = {
      strengths: ['Enforceable IP with 2 granted patents', '5 peer-reviewed publications'],
      risks_and_bottlenecks: ['Early TRL validation required before pilot testing'],
      market_opportunities: ['$5.0M in active grant solicitations identified'],
      barriers_to_entry: ['Competitor assignee density in target technology sector'],
    };

    const roadmap: RoadmapPhaseItem[] = [
      {
        phase_name: 'Phase 1: Foundation & De-risking',
        timeframe: 'Months 0-6',
        description: 'Provisional patent filings and grant proposal submissions.',
        actions: [
          {
            action: 'File provisional patent application',
            owner_role: 'PI / TTO',
            target_timeline: 'Month 2',
            expected_outcome: 'Secured priority date',
          },
        ],
      },
    ];

    const dossier: ExecutiveDossierResponse = {
      report_id: 'DOSSIER-A1B2C3D4',
      generated_at: new Date().toISOString(),
      target_name: 'Quantum Computing',
      target_type: 'DOMAIN',
      executive_summary: 'Comprehensive executive intelligence dossier for Quantum Computing.',
      key_findings: [
        'Composite Innovation Score: 78.5 / 100.',
        'Commercialization Readiness: 72.0 / 100.',
        'Primary Pathway: STARTUP_SPINOUT.',
      ],
      innovation_score: 78.5,
      innovation_classification: 'BREAKTHROUGH_INNOVATION',
      estimated_trl: 6,
      trl_stage: 'System Demonstration',
      commercialization_readiness: 72.0,
      readiness_level: 'HIGH_COMMERCIAL_READINESS',
      primary_commercial_pathway: 'STARTUP_SPINOUT',
      publication_metrics: {
        total_publications: 5,
        recent_publications: 4,
        total_citations: 95,
        average_citations: 19.0,
        venue_count: 3,
        novelty_score: 82.0,
      },
      patent_metrics: {
        total_patents: 3,
        granted_patents: 2,
        jurisdiction_count: 2,
        assignee_count: 2,
        patent_strength_score: 75.0,
      },
      funding_metrics: {
        matching_opportunities_count: 3,
        total_identified_grant_pool: 7500000.0,
        funding_relevance_score: 80.0,
      },
      whitespace_metrics: {
        detected_whitespace_count: 2,
        top_whitespace_areas: ['Topological Transmon Qubits'],
      },
      strategic_assessment: assessment,
      roadmap: roadmap,
      top_recommendations: [
        {
          recommendation_type: 'STARTUP_SPINOUT',
          title: 'Form Venture Spinout',
          priority: 'HIGH',
          score: 85.0,
          confidence: 'HIGH',
          rationale: 'High innovation score and prototype readiness favor new venture.',
          required_next_actions: ['Engage TTO for option agreement'],
        },
      ],
      top_funding_opportunities: [],
      data_sufficiency: 'SUFFICIENT',
      governance_disclaimer:
        'This Executive Intelligence Dossier is an automated synthesis of empirical publication, patent, grant, and growth metadata. It provides strategic advisory decision support and does not constitute a legal freedom-to-operate opinion, binding valuation, or guaranteed commercial success forecast.',
    };

    expect(dossier.report_id).toContain('DOSSIER-');
    expect(dossier.innovation_score).toBe(78.5);
    expect(dossier.commercialization_readiness).toBe(72.0);
    expect(dossier.strategic_assessment.strengths.length).toBe(2);
    expect(dossier.roadmap.length).toBe(1);
    expect(dossier.governance_disclaimer).toContain('Executive Intelligence Dossier');
  });

  it('validates roadmap action items and ownership roles', () => {
    const phase: RoadmapPhaseItem = {
      phase_name: 'Phase 2: Validation & Partnering',
      timeframe: 'Months 6-18',
      description: 'Pilot testbed and industry collaboration agreements.',
      actions: [
        {
          action: 'Execute Joint Development Agreement',
          owner_role: 'Innovation Manager',
          target_timeline: 'Month 12',
          expected_outcome: 'Validated prototype in operating environment',
        },
      ],
    };

    expect(phase.actions[0].owner_role).toBe('Innovation Manager');
    expect(phase.actions[0].target_timeline).toBe('Month 12');
  });
});
