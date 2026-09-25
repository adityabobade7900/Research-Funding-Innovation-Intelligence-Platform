'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  CommercializationResponse,
  CommercializationSummary,
} from '@/types/commercialization';

export default function CommercializationPage() {
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('Quantum Computing');
  const [commData, setCommData] = useState<CommercializationResponse | null>(null);
  const [summaryData, setSummaryData] = useState<CommercializationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activePathwayTab, setActivePathwayTab] = useState<'PRODUCTIZATION' | 'LICENSING' | 'STARTUP_CREATION' | 'INDUSTRY_PARTNERSHIP'>('PRODUCTIZATION');

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
        api.get<{ data: CommercializationResponse }>(`/commercialization/recommendations${queryStr}`),
        api.get<{ data: CommercializationSummary }>('/commercialization/summary'),
      ]);

      setCommData(commRes.data.data);
      setSummaryData(sumRes.data.data);

      // Default active pathway to primary pathway if mapped
      const prim = commRes.data.data.readiness.primary_pathway;
      if (prim === 'LICENSING') {
        setActivePathwayTab('LICENSING');
      } else if (prim === 'STARTUP_CREATION' || prim === 'STARTUP_SPINOUT') {
        setActivePathwayTab('STARTUP_CREATION');
      } else if (prim === 'INDUSTRY_PARTNERSHIP' || prim === 'INDUSTRY_COLLABORATION') {
        setActivePathwayTab('INDUSTRY_PARTNERSHIP');
      } else {
        setActivePathwayTab('PRODUCTIZATION');
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

  const defaultDomains = [
    'Quantum Computing',
    'Artificial Intelligence',
    'Energy Storage',
    'Biotechnology',
    'Synthetic Biology',
    'Photonics',
    'Robotics',
    'Space Propulsion',
  ];

  const allDomains = Array.from(
    new Set([
      ...defaultDomains,
      ...(summaryData?.top_commercial_prospects.map((d) => d.domain) || []),
    ])
  );

  const pathways = commData?.pathways;
  const analysis = commData?.commercialization_analysis;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Commercialization & Translation Intelligence
            </span>
            <span className="text-xs text-slate-400">
              Four Canonical Pathways: Productization • Licensing • Startup Creation • Industry Partnership
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">
            Commercialization Pathways & Evidence-Based Translation
          </h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Transforms empirical evidence from Research Intelligence, Funding, Patent Landscape, Technology Intelligence, and Innovation Scoring into actionable, non-dilutive commercialization roadmaps.
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-44" />
          ))}
        </div>
      ) : (
        <>
          {/* Main KPI Strip — Multi-Module Telemetry */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* 1. Commercialization Readiness */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm relative overflow-hidden">
              <span className="text-[11px] text-slate-400 font-medium block">Commercialization Readiness</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-4xl font-extrabold text-emerald-400">
                  {commData?.readiness.readiness_score ?? 0}
                </span>
                <span className="text-xs text-slate-500 font-medium">/ 100</span>
              </div>
              <div className="mt-3 flex items-center gap-1.5">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                  commData?.readiness.readiness_level === 'HIGH_COMMERCIAL_READINESS'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : commData?.readiness.readiness_level === 'MODERATE_COMMERCIAL_READINESS'
                    ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                    : commData?.readiness.readiness_level === 'EARLY_DEVELOPMENT'
                    ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                }`}>
                  {commData?.readiness.readiness_level.replace(/_/g, ' ')}
                </span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-slate-950 border border-slate-800 text-slate-400">
                  {commData?.readiness.data_sufficiency}
                </span>
              </div>
            </div>

            {/* 2. Innovation Score & TRL (M7 Integration) */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">M7 Innovation Index & TRL</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-2xl font-bold text-white">
                  {commData?.innovation_context.innovation_score} <span className="text-xs text-slate-500">/ 100</span>
                </span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-mono">
                  TRL {commData?.innovation_context.estimated_trl}
                </span>
              </div>
              <span className="text-[10px] text-slate-300 block mt-2 truncate">
                Stage: <strong>{commData?.innovation_context.trl_stage}</strong>
              </span>
              <span className="text-[10px] text-slate-500 block mt-1">
                Class: {commData?.innovation_context.overall_classification.replace(/_/g, ' ')}
              </span>
            </div>

            {/* 3. Adoption Level & Market Velocity (M6 Integration) */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">M6 Commercial Adoption</span>
              <div className="mt-2">
                <span className="px-2 py-1 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 block text-center font-mono">
                  DATA_UNAVAILABLE
                </span>
              </div>
              <p className="text-[10px] text-slate-400 mt-2 leading-relaxed">
                External revenue and enterprise sales are unindexed; empirical patent momentum proxy used.
              </p>
            </div>

            {/* 4. Target Focus & Evaluated Scope */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-sm">
              <span className="text-[11px] text-slate-400 font-medium block">Evaluated Target Focus</span>
              <h3 className="text-base font-bold text-white mt-1 truncate">
                {commData?.target_name}
              </h3>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-semibold">
                  Scope: {commData?.target_type}
                </span>
                <span className="text-[10px] text-slate-500">
                  • Primary: <strong className="text-slate-300">{commData?.readiness.primary_pathway.replace(/_/g, ' ')}</strong>
                </span>
              </div>
            </div>
          </div>

          {/* Commercialization Analysis — Problem / Application Fit */}
          {analysis && (
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                <div>
                  <span className="text-[10px] text-indigo-400 font-semibold uppercase tracking-wider block">
                    Domain Translation Analysis
                  </span>
                  <h3 className="text-base font-bold text-white">Problem / Application Fit Analysis</h3>
                </div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-950 text-slate-400 border border-slate-800">
                    Adoption: {analysis.commercial_adoption_telemetry}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Potential Application Areas */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-cyan-400 block">Identified Potential Application Areas:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.potential_application_areas.length > 0 ? (
                      analysis.potential_application_areas.map((area, idx) => (
                        <span
                          key={idx}
                          className="px-2.5 py-1 rounded-lg text-xs bg-cyan-950/40 text-cyan-300 border border-cyan-800/60"
                        >
                          {area}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-500">No application areas substantiated by indexed records.</span>
                    )}
                  </div>

                  <span className="text-xs font-bold text-slate-300 block pt-2">Relevant Industries:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.relevant_industries.map((ind, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded text-[11px] bg-slate-900 text-slate-300 border border-slate-800"
                      >
                        {ind}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Analytical Synthesis & Fit */}
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-indigo-400 block">Problem / Application Fit Rationale:</span>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {analysis.problem_application_fit}
                  </p>

                  <span className="text-xs font-bold text-slate-400 block pt-1">Analytical Telemetry Evidence:</span>
                  <ul className="space-y-1">
                    {analysis.supporting_evidence.map((ev, idx) => (
                      <li key={idx} className="text-xs text-slate-400 flex items-start gap-1.5">
                        <span className="text-indigo-400">•</span>
                        <span>{ev}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Data Limitations Box */}
              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
                <span className="font-semibold text-slate-300 block">Traceability & Data Limitations:</span>
                <ul className="list-disc list-inside space-y-0.5 text-slate-500">
                  {analysis.data_limitations.map((lim, idx) => (
                    <li key={idx}>{lim}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* ========================================================= */}
          {/* THE FOUR CANONICAL COMMERCIALIZATION PATHWAYS              */}
          {/* ========================================================= */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <span className="text-[10px] text-emerald-400 font-semibold uppercase tracking-wider block">
                  Authoritative Translation Pathways
                </span>
                <h2 className="text-lg font-bold text-white">Commercialization Pathways</h2>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                Evaluated deterministically from published research, patents, and grant streams
              </span>
            </div>

            {/* Pathway Selector Tabs */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {[
                { key: 'PRODUCTIZATION', label: '1. Productization', icon: '🚀' },
                { key: 'LICENSING', label: '2. Corporate Licensing', icon: '📜' },
                { key: 'STARTUP_CREATION', label: '3. Startup Creation', icon: '💡' },
                { key: 'INDUSTRY_PARTNERSHIP', label: '4. Industry Partnership', icon: '🤝' },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActivePathwayTab(tab.key as any)}
                  className={`p-3.5 rounded-xl border text-left transition flex items-center justify-between ${
                    activePathwayTab === tab.key
                      ? 'bg-indigo-950/70 border-indigo-400 text-white shadow-lg ring-1 ring-indigo-400/40'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  <div>
                    <span className="text-sm block">{tab.icon} {tab.label}</span>
                  </div>
                  <span className="text-xs font-mono text-indigo-300">
                    {tab.key === 'PRODUCTIZATION'
                      ? `${pathways?.productization.score ?? 0} pts`
                      : tab.key === 'LICENSING'
                      ? `${pathways?.licensing.score ?? 0} pts`
                      : tab.key === 'STARTUP_CREATION'
                      ? `${pathways?.startup_creation.score ?? 0} pts`
                      : `${pathways?.industry_partnership.score ?? 0} pts`}
                  </span>
                </button>
              ))}
            </div>

            {/* TAB CONTENT: 1. PRODUCTIZATION */}
            {activePathwayTab === 'PRODUCTIZATION' && pathways?.productization && (
              <div className="bg-slate-900/90 border border-indigo-500/40 p-6 rounded-2xl space-y-4 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                        PATHWAY 1: PRODUCTIZATION
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        pathways.productization.data_status === 'AVAILABLE'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {pathways.productization.data_status}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mt-1.5">{pathways.productization.product_concept}</h3>
                    <span className="text-xs text-slate-400">Target Industry: <strong className="text-slate-300">{pathways.productization.target_industry}</strong></span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Viability Score:</span>
                    <span className="text-2xl font-bold text-emerald-400">{pathways.productization.score} / 100</span>
                    <span className="text-[10px] text-slate-500 block">({pathways.productization.confidence} Confidence)</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-indigo-400 block">Problem Addressed:</span>
                    <p className="text-xs text-slate-300 leading-relaxed">{pathways.productization.problem_addressed}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Primary Deployment Use Case:</span>
                    <p className="text-xs text-slate-300">{pathways.productization.main_use_case}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Technology Basis:</span>
                    <p className="text-xs text-slate-400 font-mono text-[11px]">{pathways.productization.technology_basis}</p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-emerald-400 block">Required Next Steps:</span>
                    <ul className="space-y-1.5">
                      {pathways.productization.required_next_steps.map((step, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Supporting Analytical Evidence:</span>
                    <ul className="space-y-1">
                      {pathways.productization.supporting_evidence.map((ev, idx) => (
                        <li key={idx} className="text-xs text-slate-400 flex items-start gap-1.5">
                          <span className="text-indigo-400">•</span>
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <p className="text-[10px] text-slate-500 italic pt-1">{pathways.productization.limitations}</p>
              </div>
            )}

            {/* TAB CONTENT: 2. LICENSING */}
            {activePathwayTab === 'LICENSING' && pathways?.licensing && (
              <div className="bg-slate-900/90 border border-indigo-500/40 p-6 rounded-2xl space-y-4 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                        PATHWAY 2: CORPORATE IP LICENSING
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        pathways.licensing.data_status === 'AVAILABLE'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {pathways.licensing.data_status}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mt-1.5">{pathways.licensing.title}</h3>
                    <p className="text-xs text-slate-300 mt-1">{pathways.licensing.rationale}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Licensing Viability:</span>
                    <span className="text-2xl font-bold text-emerald-400">{pathways.licensing.score} / 100</span>
                    <span className="text-[10px] text-slate-500 block">({pathways.licensing.confidence} Confidence)</span>
                  </div>
                </div>

                {/* Potential Licensing Candidates from Module 5 Patent Assignees */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400 block">
                      Potential Licensing Candidates (Derived from Module 5 Patent Assignees):
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {pathways.licensing.licensing_candidates.length} Candidate(s) Identified
                    </span>
                  </div>

                  {pathways.licensing.licensing_candidates.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {pathways.licensing.licensing_candidates.map((cand, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white">{cand.organization}</span>
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-mono">
                              {cand.patent_count} related patent(s)
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">{cand.evidence_of_relevance}</p>
                          <div className="pt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                            <span className="text-slate-500">Status: Potential licensing candidate</span>
                            <span className="text-emerald-400">{cand.confidence} fit</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-500">
                      No corporate patent assignees currently indexed in this technology domain to qualify as licensing candidates.
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-slate-400 block">IP Defensibility Basis:</span>
                    <p className="text-xs text-slate-300">{pathways.licensing.ip_ownership_basis}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Supporting Analytical Evidence:</span>
                    <ul className="space-y-1">
                      {pathways.licensing.supporting_evidence.map((ev, idx) => (
                        <li key={idx} className="text-xs text-slate-400 flex items-start gap-1.5">
                          <span className="text-indigo-400">•</span>
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-emerald-400 block">Prescribed Next Licensing Actions:</span>
                    <ul className="space-y-1.5">
                      {pathways.licensing.required_next_steps.map((step, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <p className="text-[10px] text-slate-500 italic pt-1">{pathways.licensing.limitations}</p>
              </div>
            )}

            {/* TAB CONTENT: 3. STARTUP CREATION */}
            {activePathwayTab === 'STARTUP_CREATION' && pathways?.startup_creation && (
              <div className="bg-slate-900/90 border border-indigo-500/40 p-6 rounded-2xl space-y-4 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                        PATHWAY 3: STARTUP CREATION
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        pathways.startup_creation.data_status === 'AVAILABLE'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {pathways.startup_creation.data_status}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mt-1.5">{pathways.startup_creation.startup_concept}</h3>
                    <p className="text-xs text-slate-300 mt-1">{pathways.startup_creation.proposed_solution}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Startup Fit Score:</span>
                    <span className="text-2xl font-bold text-emerald-400">{pathways.startup_creation.score} / 100</span>
                    <span className="text-[10px] text-slate-500 block">({pathways.startup_creation.confidence} Confidence)</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-indigo-400 block">Unaddressed Market Problem:</span>
                    <p className="text-xs text-slate-300">{pathways.startup_creation.problem}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Target Customer Segment:</span>
                    <p className="text-xs text-slate-300">{pathways.startup_creation.target_customers}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Business Model Hypothesis:</span>
                    <p className="text-xs text-slate-300 leading-relaxed">{pathways.startup_creation.business_model_hypothesis}</p>

                    <span className="text-xs font-bold text-slate-400 block pt-1">Intellectual Property & Defensibility:</span>
                    <p className="text-xs text-slate-400 font-mono text-[11px]">{pathways.startup_creation.patent_ip_situation}</p>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-cyan-400 block">Matching Non-Dilutive Translational Grants:</span>
                    <ul className="space-y-1">
                      {pathways.startup_creation.relevant_funding.map((f, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-1.5">
                          <span className="text-cyan-400">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>

                    <span className="text-xs font-bold text-emerald-400 block pt-2">Venture Formation Next Steps:</span>
                    <ul className="space-y-1.5">
                      {pathways.startup_creation.required_next_steps.map((step, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <p className="text-[10px] text-slate-500 italic pt-1">{pathways.startup_creation.limitations}</p>
              </div>
            )}

            {/* TAB CONTENT: 4. INDUSTRY PARTNERSHIP */}
            {activePathwayTab === 'INDUSTRY_PARTNERSHIP' && pathways?.industry_partnership && (
              <div className="bg-slate-900/90 border border-indigo-500/40 p-6 rounded-2xl space-y-4 shadow-xl">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                        PATHWAY 4: INDUSTRY PARTNERSHIP
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        pathways.industry_partnership.data_status === 'AVAILABLE'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {pathways.industry_partnership.data_status}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mt-1.5">{pathways.industry_partnership.title}</h3>
                    <p className="text-xs text-slate-300 mt-1">{pathways.industry_partnership.rationale}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Partnership Fit Score:</span>
                    <span className="text-2xl font-bold text-emerald-400">{pathways.industry_partnership.score} / 100</span>
                    <span className="text-[10px] text-slate-500 block">({pathways.industry_partnership.confidence} Confidence)</span>
                  </div>
                </div>

                {/* Potential Industry Partnership Candidates */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400 block">
                      Potential Industry Partnership Candidates:
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {pathways.industry_partnership.partnership_candidates.length} Candidate(s) Identified
                    </span>
                  </div>

                  {pathways.industry_partnership.partnership_candidates.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {pathways.industry_partnership.partnership_candidates.map((cand, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white">{cand.organization}</span>
                            <span className="px-2 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800/60 font-medium">
                              {cand.partnership_type}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400">{cand.evidence_of_relevance}</p>
                          <div className="pt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                            <span className="text-slate-500">Status: Potential candidate for evaluation</span>
                            <span className="text-emerald-400">{cand.confidence} fit</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-500">
                      No corporate partner organizations are currently indexed in this technology domain to qualify as partnership candidates.
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-slate-400 block">Supporting Analytical Evidence:</span>
                    <ul className="space-y-1">
                      {pathways.industry_partnership.supporting_evidence.map((ev, idx) => (
                        <li key={idx} className="text-xs text-slate-400 flex items-start gap-1.5">
                          <span className="text-indigo-400">•</span>
                          <span>{ev}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-emerald-400 block">Partnership Next Steps:</span>
                    <ul className="space-y-1.5">
                      {pathways.industry_partnership.required_next_steps.map((step, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">✓</span>
                          <span>{step}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <p className="text-[10px] text-slate-500 italic pt-1">{pathways.industry_partnership.limitations}</p>
              </div>
            )}
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

              {/* Unmeasured Dimensions Box (Honest Telemetry) */}
              <div className="pt-2 border-t border-slate-800">
                <span className="text-[10px] text-slate-400 font-semibold block mb-1.5">
                  External Governance & Feasibility Telemetry (Unmeasured):
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                    <span className="text-[11px] text-slate-400">Regulatory Feasibility</span>
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      DATA_UNAVAILABLE
                    </span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
                    <span className="text-[11px] text-slate-400">Team Capability</span>
                    <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      DATA_UNAVAILABLE
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Active Matching Funding Opportunities (Module 4 Integration) */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Matching Translational Funding Streams</h3>
                <span className="text-xs text-slate-400">Module 4 Integration</span>
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
            'Commercialization recommendations and readiness scores are empirical advisory guidelines derived from patent, research, funding, and growth metadata. They represent potential commercialization pathways for further diligence and do not constitute legal patentability opinions, freedom-to-operate guarantees, or financial investment advice.'}
        </p>
      </div>
    </div>
  );
}
