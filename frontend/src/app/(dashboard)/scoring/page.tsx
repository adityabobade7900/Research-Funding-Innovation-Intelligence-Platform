'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  InnovationScoreResponse,
  InnovationScoringSummary,
  PillarScoreItem,
} from '@/types/innovation_scoring';

export default function InnovationScoringPage() {
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('Quantum Technologies');
  const [scoreData, setScoreData] = useState<InnovationScoreResponse | null>(null);
  const [summaryData, setSummaryData] = useState<InnovationScoringSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedPillarKey, setSelectedPillarKey] = useState<string>('research_novelty');

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

      const scoreQuery = params.toString() ? `?${params.toString()}` : '';

      const [scoreRes, sumRes] = await Promise.all([
        api.get<{ data: InnovationScoreResponse }>(`/innovation-scoring/score${scoreQuery}`),
        api.get<{ data: InnovationScoringSummary }>('/innovation-scoring/summary'),
      ]);

      setScoreData(scoreRes.data.data);
      setSummaryData(sumRes.data.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to compute innovation scores');
    } finally {
      setLoading(false);
    }
  }, [myProfileOnly, selectedDomain]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const pillarsList = scoreData?.pillars
    ? [
        { key: 'research_novelty', item: scoreData.pillars.research_novelty },
        { key: 'patent_strength', item: scoreData.pillars.patent_strength },
        { key: 'technology_maturity', item: scoreData.pillars.technology_maturity },
        { key: 'market_potential', item: scoreData.pillars.market_potential },
        { key: 'funding_relevance', item: scoreData.pillars.funding_relevance },
      ]
    : [];

  const selectedPillar = pillarsList.find((p) => p.key === selectedPillarKey)?.item;

  const defaultDomains = [
    'Quantum Technologies',
    'Biotechnology & Genomic Sciences',
    'Clean Energy & Sustainability',
    'Cybersecurity & Cryptography',
  ];
  const allDomains = Array.from(
    new Set([...defaultDomains, ...(summaryData?.top_innovating_domains.map((d) => d.domain) || [])])
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              5-Pillar Innovation Engine
            </span>
            <span className="text-xs text-slate-400">
              TRL 1-9 Estimation & Multi-Factor Scoring
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Innovation Scoring & Technology Readiness (TRL)</h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Deterministic multi-factor index combining Research Novelty (30%), Patent Strength (20%), Technology Maturity (15%), Market Potential (20%), and Funding Relevance (15%).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setMyProfileOnly(!myProfileOnly)}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition flex items-center gap-2 ${
              myProfileOnly
                ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${myProfileOnly ? 'bg-indigo-400' : 'bg-slate-600'}`}></span>
            {myProfileOnly ? 'My Research Profile' : 'Domain / Global Scope'}
          </button>
        </div>
      </div>

      {/* Domain Selector Bar */}
      {!myProfileOnly && (
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs text-slate-400 whitespace-nowrap">Target Domain:</span>
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 w-full sm:w-64"
            >
              {allDomains.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div className="text-xs text-slate-400">
            Portfolio Benchmark Avg: <strong className="text-indigo-300">{summaryData?.average_innovation_score ?? 0} / 100</strong>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
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
          {/* Main KPI Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Overall Score */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl relative overflow-hidden shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Composite Innovation Score</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-4xl font-extrabold text-white">
                  {scoreData?.innovation_score ?? 0}
                </span>
                <span className="text-xs text-slate-500 font-medium">/ 100</span>
              </div>
              <div className="mt-3">
                <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                  scoreData?.overall_classification === 'BREAKTHROUGH_INNOVATION'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : scoreData?.overall_classification === 'HIGH_POTENTIAL'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : scoreData?.overall_classification === 'DEVELOPING_CAPABILITY'
                    ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}>
                  {scoreData?.overall_classification.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            {/* Estimated TRL */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Estimated Technology Readiness</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-4xl font-extrabold text-indigo-400">
                  TRL {scoreData?.trl.estimated_trl ?? 1}
                </span>
                <span className="text-xs text-slate-500 font-medium">/ 9</span>
              </div>
              <span className="text-xs text-slate-300 font-medium block mt-2 truncate">
                {scoreData?.trl.trl_name}
              </span>
              <span className="text-[10px] text-slate-500 block mt-0.5">
                Stage: <strong className="text-slate-400">{scoreData?.trl.trl_stage}</strong>
              </span>
            </div>

            {/* Data Sufficiency */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Data Sufficiency Status</span>
              <div className="mt-2">
                <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                  scoreData?.data_sufficiency === 'SUFFICIENT'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : scoreData?.data_sufficiency === 'PARTIAL_EVIDENCE'
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                }`}>
                  {scoreData?.data_sufficiency.replace(/_/g, ' ')}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 mt-3 leading-relaxed">
                {scoreData?.data_sufficiency === 'SUFFICIENT'
                  ? 'Multi-stream publication & patent data available for high confidence.'
                  : scoreData?.data_sufficiency === 'PARTIAL_EVIDENCE'
                  ? 'Single-source records evaluated with analytical proxy estimators.'
                  : 'Sparse dataset; baseline heuristic calculations applied.'}
              </p>
            </div>

            {/* Target Scope */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Evaluated Target</span>
              <h3 className="text-base font-bold text-white mt-1 truncate">
                {scoreData?.target_name}
              </h3>
              <span className="text-[10px] text-indigo-400 uppercase tracking-wider block mt-1">
                Scope: {scoreData?.target_type}
              </span>
              <span className="text-[10px] text-slate-500 block mt-2">
                Statistical Confidence: <strong className="text-slate-300">{scoreData?.trl.confidence}</strong>
              </span>
            </div>
          </div>

          {/* 5-Pillar Scoreboard & Drill-down */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left 2 Cols: 5 Pillar Cards */}
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center justify-between pb-1">
                <h3 className="text-sm font-bold text-white">Five Innovation Pillars (Exact Specification Weights)</h3>
                <span className="text-xs text-slate-400 font-mono">Sum: 100%</span>
              </div>

              <div className="space-y-3">
                {pillarsList.map(({ key, item }) => (
                  <div
                    key={key}
                    onClick={() => setSelectedPillarKey(key)}
                    className={`p-4 rounded-2xl border transition duration-200 cursor-pointer ${
                      selectedPillarKey === key
                        ? 'bg-indigo-950/40 border-indigo-500 shadow-md'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-xl bg-slate-950 flex items-center justify-center text-xs font-bold text-indigo-400 border border-slate-800">
                          {Math.round(item.weight * 100)}%
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-bold text-slate-200">{item.pillar_name}</h4>
                            <span className={`px-1.5 py-0.2 rounded text-[9px] font-semibold border ${
                              item.data_status === 'AVAILABLE'
                                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                                : item.data_status === 'DATA_UNAVAILABLE'
                                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                                : 'bg-slate-800 text-slate-400 border-slate-700'
                            }`}>
                              {item.data_status.replace(/_/g, ' ')}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-400 font-mono">
                            Confidence: {item.confidence} {item.is_proxy && '• Empirical Proxy'}
                          </span>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="flex items-baseline justify-end gap-1.5">
                          <span className="text-xl font-bold text-white">{item.score}</span>
                          <span className="text-xs text-slate-400">/ 100</span>
                        </div>
                        <span className="text-[10px] text-indigo-300 block font-mono">
                          +{item.weighted_score} pts
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-2 rounded-full bg-slate-950 mt-3 overflow-hidden border border-slate-800/80">
                      <div
                        style={{ width: `${Math.min(100, Math.max(2, item.score))}%` }}
                        className={`h-full rounded-full ${
                          item.score >= 70
                            ? 'bg-gradient-to-r from-emerald-500 to-cyan-500'
                            : item.score >= 40
                            ? 'bg-gradient-to-r from-indigo-500 to-cyan-500'
                            : 'bg-gradient-to-r from-amber-500 to-rose-500'
                        }`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Col: Pillar Evidence & Signal Drill-down */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4 shadow-sm">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <span className="text-[10px] text-indigo-400 font-semibold uppercase tracking-wider block">
                    Pillar Drill-down
                  </span>
                  <h3 className="text-base font-bold text-white">{selectedPillar?.pillar_name}</h3>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                    selectedPillar?.data_status === 'AVAILABLE'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      : selectedPillar?.data_status === 'DATA_UNAVAILABLE'
                      ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      : 'bg-slate-800 text-slate-400 border-slate-700'
                  }`}>
                    {selectedPillar?.data_status?.replace(/_/g, ' ') || 'AVAILABLE'}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-950 border border-slate-800 text-slate-300">
                    Weight: {Math.round((selectedPillar?.weight ?? 0) * 100)}%
                  </span>
                </div>
              </div>

              {/* Signals */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-slate-300 block">Contributing Empirical Signals:</span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {selectedPillar?.contributing_signals &&
                    Object.entries(selectedPillar.contributing_signals).map(([sigKey, sigVal]) => (
                      <div key={sigKey} className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80">
                        <span className="text-[10px] text-slate-500 block truncate capitalize">
                          {sigKey.replace(/_/g, ' ')}
                        </span>
                        <span className="font-bold text-slate-200 mt-0.5 block truncate">
                          {typeof sigVal === 'number' ? sigVal : String(sigVal)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              {/* Evidence */}
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <span className="text-xs font-semibold text-slate-300 block">Supporting Evidence:</span>
                <ul className="space-y-1.5">
                  {selectedPillar?.evidence.map((ev, idx) => (
                    <li key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                      <span className="text-indigo-400 text-xs mt-0.5">•</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Normalization & Methodology Notes */}
              <div className="pt-2 border-t border-slate-800 space-y-1.5">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                  Normalization Method:
                </span>
                <p className="text-[11px] text-indigo-300 bg-slate-950/90 p-2 rounded-xl border border-slate-800/80 font-mono">
                  {selectedPillar?.normalization_method}
                </p>
                <p className="text-[10px] text-slate-500 italic">
                  {selectedPillar?.methodology_notes}
                </p>
              </div>
            </div>
          </div>

          {/* TRL 1-9 Visual Stage Meter */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div>
                <h3 className="text-sm font-bold text-white">Technology Readiness Level (TRL 1-9) Estimation</h3>
                <p className="text-xs text-slate-400">
                  Deterministic 9-stage evaluation heuristic informed by NASA/DoD TRL definitions based on academic publications, patent disclosures, multi-jurisdiction filings, and assignee commercial engagement.
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">Estimated Level: </span>
                <strong className="text-indigo-400 font-bold">TRL {scoreData?.trl.estimated_trl}</strong>
              </div>
            </div>

            {/* 9-Stage Progress Ladder */}
            <div className="grid grid-cols-9 gap-1.5 text-center">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((lvl) => {
                const isCurrent = scoreData?.trl.estimated_trl === lvl;
                const isPast = (scoreData?.trl.estimated_trl ?? 0) >= lvl;
                return (
                  <div
                    key={lvl}
                    className={`p-2.5 rounded-xl border text-xs transition duration-200 ${
                      isCurrent
                        ? 'bg-indigo-600 border-indigo-400 text-white font-bold shadow-lg ring-2 ring-indigo-400/40'
                        : isPast
                        ? 'bg-slate-950/80 border-indigo-900/50 text-indigo-300'
                        : 'bg-slate-950/30 border-slate-800/60 text-slate-600'
                    }`}
                  >
                    <span className="block text-xs font-mono">TRL {lvl}</span>
                  </div>
                );
              })}
            </div>

            {/* TRL Evidence Cards */}
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-2">
              <span className="text-xs font-semibold text-slate-200 block">TRL Evaluation Rationale & Proxy Signals:</span>
              <ul className="space-y-1">
                {scoreData?.trl.evidence.map((ev, idx) => (
                  <li key={idx} className="text-xs text-slate-400 flex items-start gap-2">
                    <span className="text-cyan-400">•</span>
                    <span>{ev}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Cross-Domain Innovation Benchmark Leaderboard */}
          {summaryData?.top_innovating_domains && summaryData.top_innovating_domains.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Cross-Domain Innovation Leaderboard</h3>
                <span className="text-xs text-slate-400 font-mono">
                  {summaryData.top_innovating_domains.length} Domains Evaluated
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Technology Domain</th>
                      <th className="pb-2 font-medium">Innovation Score</th>
                      <th className="pb-2 font-medium">Estimated TRL</th>
                      <th className="pb-2 font-medium">Data Sufficiency</th>
                      <th className="pb-2 font-medium">Indexed Patents</th>
                      <th className="pb-2 font-medium">Publications</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {summaryData.top_innovating_domains.map((dom) => (
                      <tr
                        key={dom.domain}
                        onClick={() => setSelectedDomain(dom.domain)}
                        className="hover:bg-slate-950/50 cursor-pointer transition"
                      >
                        <td className="py-2.5 font-semibold text-slate-200">{dom.domain}</td>
                        <td className="py-2.5 font-bold text-indigo-400">{dom.innovation_score} / 100</td>
                        <td className="py-2.5 font-mono text-cyan-400">TRL {dom.estimated_trl}</td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            dom.data_sufficiency === 'SUFFICIENT'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : 'bg-amber-500/10 text-amber-400'
                          }`}>
                            {dom.data_sufficiency}
                          </span>
                        </td>
                        <td className="py-2.5 text-slate-300">{dom.patent_count}</td>
                        <td className="py-2.5 text-slate-300">{dom.publication_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Governance & Legal Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-400 text-xs leading-relaxed space-y-1">
        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
          <span>⚖️</span> Innovation Scoring Governance & Compliance Notice
        </p>
        <p>
          {scoreData?.governance_disclaimer ||
            'The Innovation Score is an explainable composite index based on empirical research, patent, market velocity, and funding metadata. It does not constitute a legal patentability opinion, freedom-to-operate assessment, or guaranteed commercial viability prediction.'}
        </p>
      </div>
    </div>
  );
}
