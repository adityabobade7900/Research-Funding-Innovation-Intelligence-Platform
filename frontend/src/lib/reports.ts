import { ReportType, ReportFilterRequest, ReportFactorItem } from '@/types/executive_report';

export interface ReportTypeMetadata {
  type: ReportType;
  label: string;
  badge: string;
  description: string;
  moduleOrigin: string;
  iconName: string;
}

export const SUPPORTED_REPORT_TYPES: ReportTypeMetadata[] = [
  {
    type: 'FUNDING',
    label: 'Funding Intelligence',
    badge: 'M4 Pipeline',
    description: 'Grant solicitations, agency pools, upcoming deadlines, award sizing, and eligibility requirements.',
    moduleOrigin: 'Module 4: Funding Intelligence',
    iconName: 'currency-dollar',
  },
  {
    type: 'PATENT',
    label: 'Patent Landscape',
    badge: 'M5 IP Portfolio',
    description: 'Tracked patent disclosures, assignee distributions, classification codes, filing dates, and citation velocity.',
    moduleOrigin: 'Module 5: Patent Landscape Analysis',
    iconName: 'shield-check',
  },
  {
    type: 'RESEARCH_TREND',
    label: 'Research Trends',
    badge: 'M3 Momentum',
    description: 'Literature momentum, thematic keyword velocity, publication growth rates, and emerging topical frontiers.',
    moduleOrigin: 'Module 3: Research Intelligence',
    iconName: 'trending-up',
  },
  {
    type: 'INNOVATION_INTELLIGENCE',
    label: 'Innovation Intelligence',
    badge: 'M5-M7 5-Pillar',
    description: 'Composite Innovation Score broken down into the 5 official weighted pillars (Novelty 30%, Patents 20%, Tech 15%, Market 20%, Funding 15%).',
    moduleOrigin: 'Modules 5, 6, 7: Innovation Scoring',
    iconName: 'sparkles',
  },
  {
    type: 'COMMERCIALIZATION',
    label: 'Commercialization Pathways',
    badge: 'M8 Translation',
    description: 'Readiness evaluation across Productization, Licensing, Startup Spinout, and Industry Partnership pathways with conservative guidelines.',
    moduleOrigin: 'Module 8: Commercialization Recommendation',
    iconName: 'rocket-launch',
  },
  {
    type: 'EXECUTIVE_DOSSIER',
    label: 'Executive Strategic Dossier',
    badge: 'M9 Synthesis',
    description: 'Comprehensive cross-module executive briefing with SWOT assessment, roadmap phases, and portfolio benchmarks.',
    moduleOrigin: 'Module 9: Executive Dashboard',
    iconName: 'document-text',
  },
];

export function validateReportFilters(filters: Partial<ReportFilterRequest>): { isValid: boolean; error?: string } {
  if (filters.start_year && filters.end_year && filters.start_year > filters.end_year) {
    return { isValid: false, error: 'Start year cannot be greater than end year' };
  }
  if (filters.min_amount !== undefined && filters.max_amount !== undefined && filters.min_amount > filters.max_amount) {
    return { isValid: false, error: 'Minimum amount cannot exceed maximum amount' };
  }
  if (filters.min_amount !== undefined && filters.min_amount < 0) {
    return { isValid: false, error: 'Minimum amount cannot be negative' };
  }
  return { isValid: true };
}

export function verifyInnovationFactorWeights(factors: ReportFactorItem[]): boolean {
  if (!factors || factors.length !== 5) return false;
  const total = factors.reduce((sum, f) => sum + f.weight_pct, 0);
  return Math.abs(total - 100.0) < 0.01;
}
