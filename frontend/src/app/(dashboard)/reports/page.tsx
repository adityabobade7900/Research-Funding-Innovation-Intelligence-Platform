'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  ExecutiveDossierResponse,
  ExecutiveDossierSummary,
} from '@/types/executive_report';

export default function ExecutiveReportsPage() {
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('Quantum Computing');
  const [dossierData, setDossierData] = useState<ExecutiveDossierResponse | null>(null);
  const [summaryData, setSummaryData] = useState<ExecutiveDossierSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (myProfileOnly) {
        params.append('my_profile_only', 'true');
      } else if (selectedDomain) {
        params.append('domain', selectedDomain);
      }

      const queryStr = params.toString() ? `?${params.toString()}` : '';

      const [dossierRes, sumRes] = await Promise.all([
        api.get<{ data: ExecutiveDossierResponse }>(`/api/v1/reports/dossier${queryStr}`),
        api.get<{ data: ExecutiveDossierSummary }>('/api/v1/reports/summary'),
      ]);

      setDossierData(dossierRes.data.data);
      setSummaryData(sumRes.data.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to generate executive intelligence dossier');
    } finally {
      setLoading(false);
    }
  }, [myProfileOnly, selectedDomain]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDownloadMarkdown = async () => {
    try {
      setIsExporting(true);
      const params = new URLSearchParams();
      if (myProfileOnly) params.append('my_profile_only', 'true');
      else if (selectedDomain) params.append('domain', selectedDomain);
      const queryStr = params.toString() ? `?${params.toString()}` : '';

      const res = await api.get(`/api/v1/reports/export/markdown${queryStr}`, {
        responseType: 'blob',
      });
      const blob = new Blob([res.data], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Executive_Dossier_${selectedDomain.replace(/\s+/g, '_')}.md`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to export markdown report.');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadJson = () => {
    if (!dossierData) return;
    const blob = new Blob([JSON.stringify(dossierData, null, 2)], {
      type: 'application/json',
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Executive_Dossier_${selectedDomain.replace(/\s+/g, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 pb-12 print:space-y-4 print:pb-0">
      {/* Top Banner & Export Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl print:border-none print:shadow-none print:p-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Executive Reporting & Dossier Engine
            </span>
            <span className="text-xs text-slate-400">
              M4 Multi-Stream Intelligence Synthesis
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1 print:text-black">
            Executive Intelligence Dossier
          </h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1 print:hidden">
            Unified strategic synthesis combining scientific publications, patent IP landscape, translational grant pipelines, whitespace gaps, 5-pillar Innovation Scores, and commercialization roadmaps.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <button
            onClick={() => setMyProfileOnly(!myProfileOnly)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition flex items-center gap-2 ${
              myProfileOnly
                ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${myProfileOnly ? 'bg-indigo-400' : 'bg-slate-600'}`}></span>
            {myProfileOnly ? 'My Research Profile' : 'Domain Scope'}
          </button>

          <button
            onClick={handleDownloadMarkdown}
            disabled={isExporting}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200 hover:bg-slate-900 hover:border-slate-700 transition"
          >
            Export Markdown
          </button>

          <button
            onClick={handleDownloadJson}
            className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200 hover:bg-slate-900 hover:border-slate-700 transition"
          >
            Export JSON
          </button>

          <button
            onClick={handlePrint}
            className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow transition"
          >
            Print / PDF
          </button>
        </div>
      </div>

      {/* Domain Selector Bar */}
      {!myProfileOnly && (
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 print:hidden">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs text-slate-400 whitespace-nowrap">Evaluated Sector:</span>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 w-full sm:w-64"
            >
              <option value="Quantum Computing">Quantum Computing</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Energy Storage">Energy Storage</option>
              <option value="Biotechnology">Biotechnology</option>
              <option value="Photonics">Photonics</option>
              <option value="Robotics">Robotics</option>
              {summaryData?.domain_benchmarks.map((d) => (
                <option key={d.domain} value={d.domain}>
                  {d.domain}
                </option>
              ))}
            </select>
          </div>

          <div className="text-xs text-slate-400">
            Portfolio Benchmarked Sectors:{' '}
            <strong className="text-indigo-300">{summaryData?.total_domains_benchmarked ?? 0} Domains</strong>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between print:hidden">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-200 font-bold">×</button>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-48" />
          ))}
        </div>
      ) : (
        <>
          {/* Executive Dossier Hero Card */}
          <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs font-bold text-indigo-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                  {dossierData?.report_id}
                </span>
                <h2 className="text-base font-bold text-white">
                  {dossierData?.target_name} ({dossierData?.target_type})
                </h2>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-400">
                <span>Generated: {dossierData?.generated_at ? new Date(dossierData.generated_at).toLocaleDateString() : ''}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  dossierData?.data_sufficiency === 'SUFFICIENT'
                    ? 'bg-emerald-500/10 text-emerald-400'
                    : 'bg-amber-500/10 text-amber-400'
                }`}>
                  {dossierData?.data_sufficiency}
                </span>
              </div>
            </div>

            <div>
              <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-semibold block mb-1">
                Executive Synthesis
              </span>
              <p className="text-xs text-slate-300 leading-relaxed">
                {dossierData?.executive_summary}
              </p>
            </div>
          </div>

          {/* Core Metric Scoreboard (6 Tiles) */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* 1. Innovation Score */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">Innovation Score</span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-extrabold text-white">{dossierData?.innovation_score}</span>
                <span className="text-[10px] text-slate-500">/ 100</span>
              </div>
              <span className="text-[9px] text-indigo-300 block mt-1 truncate">
                {dossierData?.innovation_classification.replace(/_/g, ' ')}
              </span>
            </div>

            {/* 2. TRL Maturity */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">TRL Maturity</span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-extrabold text-indigo-400">TRL {dossierData?.estimated_trl}</span>
                <span className="text-[10px] text-slate-500">/ 9</span>
              </div>
              <span className="text-[9px] text-slate-400 block mt-1 truncate">
                {dossierData?.trl_stage}
              </span>
            </div>

            {/* 3. Commercialization Readiness */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">Commercial Readiness</span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-2xl font-extrabold text-emerald-400">{dossierData?.commercialization_readiness}</span>
                <span className="text-[10px] text-slate-500">/ 100</span>
              </div>
              <span className="text-[9px] text-emerald-300 block mt-1 truncate">
                {dossierData?.readiness_level.replace(/_/g, ' ')}
              </span>
            </div>

            {/* 4. Primary Pathway */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">Primary Pathway</span>
              <div className="text-sm font-extrabold text-white mt-1 truncate">
                {dossierData?.primary_commercial_pathway.replace(/_/g, ' ')}
              </div>
              <span className="text-[9px] text-slate-400 block mt-1">
                Prioritized Action
              </span>
            </div>

            {/* 5. Patents & Grants */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">Patent Disclosures</span>
              <div className="text-2xl font-extrabold text-cyan-400 mt-1">
                {dossierData?.patent_metrics.total_patents}
              </div>
              <span className="text-[9px] text-slate-400 block mt-1 truncate">
                {dossierData?.patent_metrics.granted_patents} Granted Claims
              </span>
            </div>

            {/* 6. Research Output */}
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm">
              <span className="text-[10px] text-slate-400 block font-medium">Indexed Papers</span>
              <div className="text-2xl font-extrabold text-white mt-1">
                {dossierData?.publication_metrics.total_publications}
              </div>
              <span className="text-[9px] text-slate-400 block mt-1 truncate">
                {dossierData?.publication_metrics.total_citations} Citations
              </span>
            </div>
          </div>

          {/* 4-Quadrant Strategic Assessment (SWOT Synthesis) */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white">Strategic Assessment (SWOT Synthesis)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Strengths */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-emerald-500/30 space-y-2">
                <div className="flex items-center gap-2 pb-1 border-b border-emerald-500/20">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <h4 className="text-xs font-bold text-emerald-400">Verified Strengths & Advantages</h4>
                </div>
                <ul className="space-y-1.5 pt-1">
                  {dossierData?.strategic_assessment.strengths.map((s, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Risks & Bottlenecks */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-rose-500/30 space-y-2">
                <div className="flex items-center gap-2 pb-1 border-b border-rose-500/20">
                  <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                  <h4 className="text-xs font-bold text-rose-400">Critical Risks & Bottlenecks</h4>
                </div>
                <ul className="space-y-1.5 pt-1">
                  {dossierData?.strategic_assessment.risks_and_bottlenecks.map((r, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-rose-400 font-bold">•</span>
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Market Opportunities */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-cyan-500/30 space-y-2">
                <div className="flex items-center gap-2 pb-1 border-b border-cyan-500/20">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <h4 className="text-xs font-bold text-cyan-400">Market & Grant Opportunities</h4>
                </div>
                <ul className="space-y-1.5 pt-1">
                  {dossierData?.strategic_assessment.market_opportunities.map((o, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-cyan-400 font-bold">•</span>
                      <span>{o}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Barriers to Entry */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-amber-500/30 space-y-2">
                <div className="flex items-center gap-2 pb-1 border-b border-amber-500/20">
                  <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                  <h4 className="text-xs font-bold text-amber-400">Barriers to Entry & Thickets</h4>
                </div>
                <ul className="space-y-1.5 pt-1">
                  {dossierData?.strategic_assessment.barriers_to_entry.map((b, idx) => (
                    <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 3-Phase Execution Roadmap */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white">Three-Phase Strategic Execution Roadmap</h3>
              <p className="text-xs text-slate-400">
                Actionable milestones mapped across near-term technical de-risking, mid-term validation, and long-term scaling.
              </p>
            </div>

            <div className="space-y-4">
              {dossierData?.roadmap.map((phase) => (
                <div key={phase.phase_name} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-indigo-300">{phase.phase_name}</h4>
                      <p className="text-[11px] text-slate-400 mt-0.5">{phase.description}</p>
                    </div>
                    <span className="px-2.5 py-0.5 rounded text-[10px] font-mono bg-slate-900 text-slate-300 border border-slate-800">
                      {phase.timeframe}
                    </span>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 text-[11px]">
                          <th className="pb-1.5 font-medium">Strategic Action</th>
                          <th className="pb-1.5 font-medium">Lead Role</th>
                          <th className="pb-1.5 font-medium">Timeline</th>
                          <th className="pb-1.5 font-medium">Target Outcome</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60">
                        {phase.actions.map((act, idx) => (
                          <tr key={idx}>
                            <td className="py-2 font-medium text-slate-200">{act.action}</td>
                            <td className="py-2 text-indigo-400">{act.owner_role}</td>
                            <td className="py-2 font-mono text-slate-400">{act.target_timeline}</td>
                            <td className="py-2 text-emerald-300">{act.expected_outcome}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Priority Recommendations */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white">Prioritized Commercialization Recommendations</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {dossierData?.top_recommendations.map((rec) => (
                <div key={rec.recommendation_type} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rec.priority === 'HIGH' ? 'bg-rose-500/10 text-rose-400' : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {rec.priority} PRIORITY
                    </span>
                    <span className="text-xs font-bold text-emerald-400">Score: {rec.score} / 100</span>
                  </div>

                  <h4 className="text-xs font-bold text-white">{rec.title}</h4>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{rec.rationale}</p>

                  <div className="pt-2 border-t border-slate-800/80">
                    <span className="text-[10px] text-indigo-300 font-semibold block mb-1">Immediate Actions:</span>
                    <ul className="space-y-1">
                      {rec.required_next_actions.slice(0, 2).map((act, idx) => (
                        <li key={idx} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cross-Domain Benchmark Summary Table */}
          {summaryData?.domain_benchmarks && summaryData.domain_benchmarks.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4 print:hidden">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Portfolio Cross-Domain Benchmark Matrix</h3>
                <span className="text-xs text-slate-400 font-mono">
                  {summaryData.domain_benchmarks.length} Sectors Audited
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Domain</th>
                      <th className="pb-2 font-medium">Innovation Score</th>
                      <th className="pb-2 font-medium">TRL Stage</th>
                      <th className="pb-2 font-medium">Readiness</th>
                      <th className="pb-2 font-medium">Dominant Pathway</th>
                      <th className="pb-2 font-medium">Patents</th>
                      <th className="pb-2 font-medium">Papers</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {summaryData.domain_benchmarks.map((bench) => (
                      <tr
                        key={bench.domain}
                        onClick={() => setSelectedDomain(bench.domain)}
                        className="hover:bg-slate-950/50 cursor-pointer transition"
                      >
                        <td className="py-2.5 font-semibold text-slate-200">{bench.domain}</td>
                        <td className="py-2.5 font-bold text-indigo-400">{bench.innovation_score} / 100</td>
                        <td className="py-2.5 font-mono text-cyan-400">TRL {bench.estimated_trl}</td>
                        <td className="py-2.5 font-bold text-emerald-400">{bench.commercialization_readiness} / 100</td>
                        <td className="py-2.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-950 text-slate-300 border border-slate-800">
                            {bench.primary_pathway.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td className="py-2.5 text-slate-300">{bench.total_patents}</td>
                        <td className="py-2.5 text-slate-300">{bench.total_publications}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Governance & Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-400 text-xs leading-relaxed space-y-1">
        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
          <span>⚖️</span> Executive Intelligence Governance & Regulatory Notice
        </p>
        <p>
          {dossierData?.governance_disclaimer ||
            'This Executive Intelligence Dossier is an automated synthesis of empirical publication, patent, grant, and growth metadata. It provides strategic advisory decision support and does not constitute a legal freedom-to-operate opinion, binding valuation, or guaranteed commercial success forecast.'}
        </p>
      </div>
    </div>
  );
}
