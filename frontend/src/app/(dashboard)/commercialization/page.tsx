'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  CommercializationResponse,
  CommercializationSummary,
  CommercializationRecommendationItem,
} from '@/types/commercialization';

export default function CommercializationPage() {
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('Quantum Computing');
  const [commData, setCommData] = useState<CommercializationResponse | null>(null);
  const [summaryData, setSummaryData] = useState<CommercializationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeRecType, setActiveRecType] = useState<string | null>(null);

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

      const [commRes, sumRes] = await Promise.all([
        api.get<{ data: CommercializationResponse }>(`/api/v1/commercialization/recommendations${queryStr}`),
        api.get<{ data: CommercializationSummary }>('/api/v1/commercialization/summary'),
      ]);

      setCommData(commRes.data.data);
      setSummaryData(sumRes.data.data);
      if (commRes.data.data.recommendations.length > 0) {
        setActiveRecType(commRes.data.data.primary_recommendation.recommendation_type);
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load commercialization intelligence');
    } finally {
      setLoading(false);
    }
  }, [myProfileOnly, selectedDomain]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const selectedRec =
    commData?.recommendations.find((r) => r.recommendation_type === activeRecType) ||
    commData?.primary_recommendation;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Commercialization & Translation Engine
            </span>
            <span className="text-xs text-slate-400">
              M3D Evidence-Based Translation Pathways
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">
            Commercialization Intelligence & Strategic Recommendations
          </h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Synthesizes TRL maturity, patent claims, market growth velocity, and active grant streams into actionable translation roadmaps (Spinout, Licensing, Industry JDA, Non-Dilutive Funding).
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
            <span className="text-xs text-slate-400 whitespace-nowrap">Focus Domain:</span>
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
              {summaryData?.top_commercial_prospects.map((d) => (
                <option key={d.domain} value={d.domain}>
                  {d.domain}
                </option>
              ))}
            </select>
          </div>

          <div className="text-xs text-slate-400">
            Portfolio Avg Readiness:{' '}
            <strong className="text-emerald-400">{summaryData?.average_readiness_score ?? 0} / 100</strong>
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
          {/* Main KPI Strip */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Commercialization Readiness */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Commercialization Readiness</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-4xl font-extrabold text-emerald-400">
                  {commData?.readiness.readiness_score ?? 0}
                </span>
                <span className="text-xs text-slate-500 font-medium">/ 100</span>
              </div>
              <div className="mt-3">
                <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                  commData?.readiness.readiness_level === 'HIGH_COMMERCIAL_READINESS'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                    : commData?.readiness.readiness_level === 'MODERATE_COMMERCIAL_READINESS'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : commData?.readiness.readiness_level === 'EARLY_DEVELOPMENT'
                    ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}>
                  {commData?.readiness.readiness_level.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            {/* Primary Suggested Pathway */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Primary Translation Pathway</span>
              <h3 className="text-base font-extrabold text-white mt-1">
                {commData?.readiness.primary_pathway.replace(/_/g, ' ')}
              </h3>
              <p className="text-[10px] text-slate-400 mt-2 leading-relaxed truncate">
                {commData?.primary_recommendation.title}
              </p>
              <span className="text-[10px] text-indigo-400 block mt-2">
                Urgency / Priority: <strong className="text-slate-200">{commData?.primary_recommendation.priority}</strong>
              </span>
            </div>

            {/* Innovation Context */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">M3C Innovation Context</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-2xl font-bold text-white">
                  {commData?.innovation_context.innovation_score} <span className="text-xs text-slate-500">/ 100</span>
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                  TRL {commData?.innovation_context.estimated_trl}
                </span>
              </div>
              <span className="text-[10px] text-slate-400 block mt-2">
                Stage: <strong className="text-slate-300">{commData?.innovation_context.trl_stage}</strong>
              </span>
              <span className="text-[10px] text-slate-500 block mt-1">
                Class: {commData?.innovation_context.overall_classification.replace(/_/g, ' ')}
              </span>
            </div>

            {/* Evaluated Target */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Target Focus</span>
              <h3 className="text-base font-bold text-white mt-1 truncate">
                {commData?.target_name}
              </h3>
              <span className="text-[10px] text-indigo-400 uppercase tracking-wider block mt-1">
                Scope: {commData?.target_type}
              </span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold inline-block mt-2 ${
                commData?.readiness.data_sufficiency === 'SUFFICIENT'
                  ? 'bg-emerald-500/10 text-emerald-400'
                  : 'bg-amber-500/10 text-amber-400'
              }`}>
                {commData?.readiness.data_sufficiency}
              </span>
            </div>
          </div>

          {/* Primary Recommendation Spotlight Card */}
          {selectedRec && (
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/40 p-6 rounded-2xl shadow-lg space-y-4">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                    selectedRec.priority === 'HIGH'
                      ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                      : selectedRec.priority === 'MEDIUM'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      : 'bg-slate-800 text-slate-300'
                  }`}>
                    {selectedRec.priority} PRIORITY
                  </span>
                  <span className="px-2.5 py-1 rounded text-xs font-mono bg-slate-950 text-indigo-300 border border-slate-800">
                    Pathway: {selectedRec.recommendation_type.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">Match Fit:</span>
                  <span className="text-base font-bold text-emerald-400">{selectedRec.score} / 100</span>
                  <span className="text-xs text-slate-500">({selectedRec.confidence} Confidence)</span>
                </div>
              </div>

              <div>
                <h2 className="text-lg font-bold text-white">{selectedRec.title}</h2>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{selectedRec.rationale}</p>
              </div>

              {/* Supporting Evidence & Required Actions Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-indigo-400 block">Supporting Analytical Evidence:</span>
                  <ul className="space-y-1.5">
                    {selectedRec.supporting_evidence.map((ev, idx) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-indigo-400">•</span>
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-emerald-400 block">Required Next Actions Checklist:</span>
                  <ul className="space-y-1.5">
                    {selectedRec.required_next_actions.map((act, idx) => (
                      <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-emerald-400 font-bold">✓</span>
                        <span>{act}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <p className="text-[10px] text-slate-500 italic pt-1">{selectedRec.limitations}</p>
            </div>
          )}

          {/* All Generated Commercialization Recommendations Cards */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-white">All Identified Commercialization Pathways</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {commData?.recommendations.map((rec) => (
                <div
                  key={rec.recommendation_type}
                  onClick={() => setActiveRecType(rec.recommendation_type)}
                  className={`p-4 rounded-2xl border cursor-pointer transition duration-200 ${
                    activeRecType === rec.recommendation_type
                      ? 'bg-indigo-950/40 border-indigo-500 shadow-md'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      rec.priority === 'HIGH'
                        ? 'bg-rose-500/10 text-rose-400'
                        : 'bg-amber-500/10 text-amber-400'
                    }`}>
                      {rec.priority}
                    </span>
                    <span className="text-xs font-bold text-indigo-300">{rec.score} / 100</span>
                  </div>

                  <h4 className="text-xs font-bold text-white mt-2">{rec.title}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{rec.rationale}</p>

                  <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500">
                    <span>{rec.recommendation_type.replace(/_/g, ' ')}</span>
                    <span className="text-indigo-400 font-medium">View Details →</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dimensional Readiness & Integrated Funding Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 5-Dimensional Readiness Breakdown */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Commercialization Readiness Dimensions</h3>
                <span className="text-xs font-mono text-emerald-400">
                  Total: {commData?.readiness.readiness_score} / 100
                </span>
              </div>

              <div className="space-y-3">
                {commData?.readiness.dimensions &&
                  Object.entries(commData.readiness.dimensions).map(([dimKey, dimScore]) => {
                    const weight =
                      dimKey === 'technology_maturity'
                        ? '30%'
                        : dimKey === 'patent_strength'
                        ? '25%'
                        : dimKey === 'market_potential'
                        ? '20%'
                        : dimKey === 'funding_relevance'
                        ? '15%'
                        : '10%';
                    return (
                      <div key={dimKey} className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-300 capitalize">{dimKey.replace(/_/g, ' ')}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] text-slate-500">Weight: {weight}</span>
                            <span className="font-bold text-white">{dimScore} / 100</span>
                          </div>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                          <div
                            style={{ width: `${Math.min(100, Math.max(2, dimScore))}%` }}
                            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-emerald-500"
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>

            {/* Active Matching Funding Opportunities (M2 Integration) */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Matching Translational Funding Streams</h3>
                <span className="text-xs text-slate-400">M2 Integration</span>
              </div>

              {commData?.funding_opportunities && commData.funding_opportunities.length > 0 ? (
                <div className="space-y-2.5">
                  {commData.funding_opportunities.map((f) => (
                    <div key={f.id} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200 truncate max-w-[280px]">{f.title}</span>
                        <span className="text-[10px] font-bold text-emerald-400">
                          {f.funding_amount ? `$${(f.funding_amount / 1000000).toFixed(1)}M` : 'Open'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1 text-[10px] text-slate-500">
                        <span>Agency: {f.funding_agency}</span>
                        <span>Deadline: {f.application_deadline ? new Date(f.application_deadline).toLocaleDateString() : 'Rolling'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500">No active funding opportunities currently match this filter.</p>
              )}
            </div>
          </div>

          {/* Cross-Domain Commercial Prospects Leaderboard */}
          {summaryData?.top_commercial_prospects && summaryData.top_commercial_prospects.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Cross-Domain Commercialization Leaderboard</h3>
                <span className="text-xs text-slate-400 font-mono">
                  {summaryData.top_commercial_prospects.length} Technology Sectors Benchmarked
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Technology Domain</th>
                      <th className="pb-2 font-medium">Readiness Score</th>
                      <th className="pb-2 font-medium">Primary Pathway</th>
                      <th className="pb-2 font-medium">TRL Stage</th>
                      <th className="pb-2 font-medium">Innovation Score</th>
                      <th className="pb-2 font-medium">Action Items</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {summaryData.top_commercial_prospects.map((prospect) => (
                      <tr
                        key={prospect.domain}
                        onClick={() => setSelectedDomain(prospect.domain)}
                        className="hover:bg-slate-950/50 cursor-pointer transition"
                      >
                        <td className="py-2.5 font-semibold text-slate-200">{prospect.domain}</td>
                        <td className="py-2.5 font-bold text-emerald-400">{prospect.readiness_score} / 100</td>
                        <td className="py-2.5">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-950 text-indigo-300 border border-slate-800">
                            {prospect.primary_pathway.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td className="py-2.5 font-mono text-cyan-400">TRL {prospect.estimated_trl}</td>
                        <td className="py-2.5 text-slate-300">{prospect.innovation_score} / 100</td>
                        <td className="py-2.5 text-slate-400">{prospect.recommendation_count} pathways</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Governance & Compliance Disclaimer */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-400 text-xs leading-relaxed space-y-1">
        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
          <span>⚖️</span> Commercialization & Venture Advisory Governance Disclaimer
        </p>
        <p>
          {commData?.governance_disclaimer ||
            'Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice.'}
        </p>
      </div>
    </div>
  );
}
