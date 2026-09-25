'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  TechnologyIntelligenceSummary,
  TechnologyActivityResponse,
  TechnologyGrowthResponse,
  TechnologyCoverageResponse,
  WhitespaceDiscoveryResponse,
  TechnologyMaturityResponse,
  TechnologyMaturityItem,
  EmergingTechnologyResponse,
  CompetitiveTechnologyResponse,
  AdoptionTrackingResponse,
} from '@/types/technology_intelligence';

export default function TechnologyIntelligencePage() {
  const [activeTab, setActiveTab] = useState<'maturity' | 'emerging' | 'whitespace' | 'growth' | 'competitive' | 'adoption'>('maturity');
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [whitespaceThreshold, setWhitespaceThreshold] = useState(45);

  const [summary, setSummary] = useState<TechnologyIntelligenceSummary | null>(null);
  const [maturityData, setMaturityData] = useState<TechnologyMaturityResponse | null>(null);
  const [emergingData, setEmergingData] = useState<EmergingTechnologyResponse | null>(null);
  const [whitespaceData, setWhitespaceData] = useState<WhitespaceDiscoveryResponse | null>(null);
  const [growthData, setGrowthData] = useState<TechnologyGrowthResponse | null>(null);
  const [activityData, setActivityData] = useState<TechnologyActivityResponse | null>(null);
  const [competitiveData, setCompetitiveData] = useState<CompetitiveTechnologyResponse | null>(null);
  const [adoptionData, setAdoptionData] = useState<AdoptionTrackingResponse | null>(null);

  const [selectedMaturityItem, setSelectedMaturityItem] = useState<TechnologyMaturityItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (myProfileOnly) params.append('my_profile_only', 'true');
      if (selectedDomain) params.append('domain', selectedDomain);
      params.append('whitespace_threshold', whitespaceThreshold.toString());

      const queryStr = params.toString() ? `?${params.toString()}` : '';

      const [sumRes, matRes, emRes, wsRes, grRes, actRes, compRes, adoptRes] = await Promise.all([
        api.get<{ data: TechnologyIntelligenceSummary }>(`/technology-intelligence/summary${queryStr}`),
        api.get<{ data: TechnologyMaturityResponse }>(`/technology-intelligence/maturity${queryStr}`),
        api.get<{ data: EmergingTechnologyResponse }>(`/technology-intelligence/emerging${queryStr}`),
        api.get<{ data: WhitespaceDiscoveryResponse }>(`/technology-intelligence/whitespace${queryStr}`),
        api.get<{ data: TechnologyGrowthResponse }>(`/technology-intelligence/growth${queryStr}`),
        api.get<{ data: TechnologyActivityResponse }>(`/technology-intelligence/activity${queryStr}`),
        api.get<{ data: CompetitiveTechnologyResponse }>(`/technology-intelligence/competitive${queryStr}`),
        api.get<{ data: AdoptionTrackingResponse }>(`/technology-intelligence/adoption${queryStr}`),
      ]);

      setSummary(sumRes.data.data);
      setMaturityData(matRes.data.data);
      setEmergingData(emRes.data.data);
      setWhitespaceData(wsRes.data.data);
      setGrowthData(grRes.data.data);
      setActivityData(actRes.data.data);
      setCompetitiveData(compRes.data.data);
      setAdoptionData(adoptRes.data.data);

      if (matRes.data.data.items.length > 0 && !selectedMaturityItem) {
        setSelectedMaturityItem(matRes.data.data.items[0]);
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load technology intelligence');
    } finally {
      setLoading(false);
    }
  }, [myProfileOnly, selectedDomain, whitespaceThreshold]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Stage Badge Helper
  const getStageBadge = (stage: string) => {
    switch (stage) {
      case 'EMERGING':
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">EMERGING</span>;
      case 'DEVELOPING':
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">DEVELOPING</span>;
      case 'MATURE':
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">MATURE</span>;
      case 'DECLINING':
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">DECLINING</span>;
      case 'INSUFFICIENT_DATA':
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">INSUFFICIENT DATA</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-500/10 text-slate-400 border border-slate-500/20">{stage}</span>;
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Module 6: Technology Intelligence
            </span>
            <span className="text-xs text-slate-400">
              Cross-Correlating Scientific Literature (M3) & Patent Landscape (M5)
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Technology Intelligence & Whitespace Discovery</h1>
          <p className="text-xs text-slate-400 max-w-3xl mt-1">
            Deterministic multi-signal technology maturity analysis (6-indicator model), research-to-patent density whitespace detection, multi-year CAGR, and competitive landscape monitoring.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setMyProfileOnly(!myProfileOnly)}
            className={`px-3 py-2 rounded-xl text-xs font-semibold border transition flex items-center gap-1.5 ${
              myProfileOnly
                ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow'
                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${myProfileOnly ? 'bg-indigo-400' : 'bg-slate-600'}`}></span>
            {myProfileOnly ? 'My Profile Scoped' : 'Global Corpus'}
          </button>
        </div>
      </div>

      {/* Disclaimers & Alert */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-200 font-bold">×</button>
        </div>
      )}

      {/* KPI Metric Strip */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Total Patents</span>
          <span className="text-xl font-bold text-white mt-1 block">
            {summary?.total_patents ?? 0}
          </span>
          <span className="text-[10px] text-cyan-400">Indexed (M5)</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Active Domains</span>
          <span className="text-xl font-bold text-indigo-400 mt-1 block">
            {maturityData?.total_domains_analyzed ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">Fields Analyzed</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Emerging Frontiers</span>
          <span className="text-xl font-bold text-amber-400 mt-1 block">
            {emergingData?.total_candidates ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">High Momentum</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Potential Whitespaces</span>
          <span className="text-xl font-bold text-rose-400 mt-1 block">
            {whitespaceData?.total_candidates ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">R2P Density Gaps</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Growing Fields</span>
          <span className="text-xl font-bold text-emerald-400 mt-1 block">
            {growthData?.total_growing_areas ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">Positive Velocity</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Adoption Tracking</span>
          <span className="text-xl font-bold text-slate-300 mt-1 block">
            Isolated
          </span>
          <span className="text-[10px] text-slate-400">Strictly Separate</span>
        </div>
      </div>

      {/* Filter and Tab Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl space-y-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 overflow-x-auto max-w-full">
            <button
              onClick={() => setActiveTab('maturity')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'maturity' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>📊</span>
              Technology Maturity ({maturityData?.items?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('emerging')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'emerging' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>🚀</span>
              Emerging Tech ({emergingData?.candidates?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('whitespace')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap flex items-center gap-1.5 ${
                activeTab === 'whitespace' ? 'bg-gradient-to-r from-amber-600 to-rose-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              Whitespace Discovery ({whitespaceData?.total_candidates ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('growth')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'growth' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Growth & CAGR ({growthData?.items?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('competitive')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'competitive' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Competitive (HHI)
            </button>
            <button
              onClick={() => setActiveTab('adoption')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'adoption' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Adoption Tracking
            </button>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Technology Domains</option>
              {maturityData?.items?.map((item) => (
                <option key={item.technology_domain} value={item.technology_domain}>
                  {item.technology_domain}
                </option>
              ))}
            </select>

            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400 whitespace-nowrap">Whitespace Sensitivity: {whitespaceThreshold}</span>
              <input
                type="range"
                min={30}
                max={90}
                step={5}
                value={whitespaceThreshold}
                onChange={(e) => setWhitespaceThreshold(parseInt(e.target.value))}
                className="w-24 accent-indigo-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Areas */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-44" />
          ))}
        </div>
      ) : (
        <>
          {/* TAB 1: TECHNOLOGY MATURITY (MENTOR 6-INDICATOR MODEL) */}
          {activeTab === 'maturity' && (
            <div className="space-y-6">
              {/* Methodology Header Callout */}
              <div className="bg-indigo-950/30 border border-indigo-500/30 p-4 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs text-indigo-200">
                <div>
                  <span className="font-bold text-white block">Mentor Mandatory Maturity Model (100% Total):</span>
                  <span className="text-slate-300">
                    Research Growth (25%) + Patent Growth (25%) + Research Activity (15%) + Patent Activity (15%) + Organization Participation (10%) + Technology Diversity (10%).
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-indigo-400">
                  <span>Stages: Emerging | Developing | Mature | Declining</span>
                </div>
              </div>

              {/* Cards Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {maturityData?.items.map((m) => (
                  <div
                    key={m.technology_domain}
                    className="bg-slate-900/70 border border-slate-800/90 hover:border-indigo-500/50 p-5 rounded-2xl transition duration-200 space-y-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          {getStageBadge(m.stage)}
                          <span className="text-[11px] text-slate-400">
                            {m.publication_count} Paper(s) • {m.patent_count} Patent(s)
                          </span>
                        </div>
                        <h3 className="text-base font-bold text-white mt-1">{m.technology_domain}</h3>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-black text-indigo-400 block">{m.maturity_score.toFixed(1)}</span>
                        <span className="text-[10px] text-slate-400">Maturity Score / 100</span>
                      </div>
                    </div>

                    {/* 6 Indicators Breakdown */}
                    <div className="space-y-2 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                      <div className="text-[11px] font-semibold text-slate-300 mb-1.5 flex justify-between">
                        <span>Six-Indicator Breakdown</span>
                        <span className="text-slate-400 text-[10px]">Weighted Contributions</span>
                      </div>

                      {/* 1. Research Growth (25%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>1. Research Growth (Weight 25%)</span>
                          <span className="font-mono text-cyan-400">{m.indicators.research_growth_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${m.indicators.research_growth_score}%` }}></div>
                        </div>
                      </div>

                      {/* 2. Patent Growth (25%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>2. Patent Growth (Weight 25%)</span>
                          <span className="font-mono text-indigo-400">{m.indicators.patent_growth_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${m.indicators.patent_growth_score}%` }}></div>
                        </div>
                      </div>

                      {/* 3. Research Activity (15%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>3. Research Activity (Weight 15%)</span>
                          <span className="font-mono text-emerald-400">{m.indicators.research_activity_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${m.indicators.research_activity_score}%` }}></div>
                        </div>
                      </div>

                      {/* 4. Patent Activity (15%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>4. Patent Activity (Weight 15%)</span>
                          <span className="font-mono text-amber-400">{m.indicators.patent_activity_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${m.indicators.patent_activity_score}%` }}></div>
                        </div>
                      </div>

                      {/* 5. Organization Participation (10%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>5. Organization Participation (Weight 10%)</span>
                          <span className="font-mono text-purple-400">{m.indicators.organization_participation_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${m.indicators.organization_participation_score}%` }}></div>
                        </div>
                      </div>

                      {/* 6. Technology Diversity (10%) */}
                      <div>
                        <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                          <span>6. Technology / App Diversity (Weight 10%)</span>
                          <span className="font-mono text-rose-400">{m.indicators.technology_diversity_score.toFixed(1)}/100</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div className="bg-rose-500 h-1.5 rounded-full" style={{ width: `${m.indicators.technology_diversity_score}%` }}></div>
                        </div>
                      </div>
                    </div>

                    {/* Explainability Summary Box */}
                    <div className="bg-slate-950/40 p-3 rounded-xl border border-slate-800/60 text-xs text-slate-300">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 block mb-1">
                        Explainability & Rationale
                      </span>
                      <p className="leading-relaxed">{m.explainability_summary}</p>
                    </div>

                    {/* Factual Evidence List */}
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                        Supporting Evidence
                      </span>
                      <ul className="space-y-1">
                        {m.evidence.map((ev, idx) => (
                          <li key={idx} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                            <span className="text-indigo-400 mt-0.5">•</span>
                            <span>{ev}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: EMERGING TECHNOLOGIES */}
          {activeTab === 'emerging' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {emergingData?.candidates.map((em) => (
                  <div
                    key={em.technology_domain}
                    className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl hover:border-amber-500/50 transition space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                        {em.growth_trajectory}
                      </span>
                      <span className="text-xl font-black text-amber-400">{em.emerging_score.toFixed(1)}</span>
                    </div>
                    <h3 className="text-base font-bold text-white">{em.technology_domain}</h3>
                    <p className="text-xs text-slate-300 leading-relaxed">{em.rationale}</p>

                    <div className="grid grid-cols-2 gap-2 text-[11px] bg-slate-950 p-2.5 rounded-xl border border-slate-800">
                      <div>
                        <span className="text-slate-400 block text-[10px]">Patent Velocity</span>
                        <span className="font-semibold text-white">{em.patent_velocity_score.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px]">Organizations</span>
                        <span className="font-semibold text-white">{em.organization_count}</span>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <span className="text-[10px] text-slate-400 uppercase font-semibold">Key Emergence Signals:</span>
                      <ul className="space-y-1">
                        {em.key_signals.map((sig, idx) => (
                          <li key={idx} className="text-[11px] text-slate-300 flex items-start gap-1">
                            <span className="text-amber-400">⚡</span>
                            <span>{sig}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: WHITESPACE DISCOVERY (RESEARCH VS PATENT) */}
          {activeTab === 'whitespace' && (
            <div className="space-y-6">
              {/* 2D Interactive Semantic Whitespace Visualization */}
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <span>🗺️</span> 2D Whitespace Semantic Map: Research Activity vs. Patent Density
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Visualizing technological whitespace: Technologies in the bottom-right quadrant exhibit high academic research momentum with sparse patent saturation.
                    </p>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span><span className="text-slate-300">Whitespace Area</span></div>
                    <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span><span className="text-slate-300">Developing</span></div>
                    <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span><span className="text-slate-300">Established</span></div>
                  </div>
                </div>

                {/* 2D Coordinate Grid Canvas */}
                <div className="relative h-64 bg-slate-950/80 rounded-xl border border-slate-800 p-4 overflow-hidden">
                  {/* Quadrant Dividers */}
                  <div className="absolute left-1/2 top-0 bottom-0 border-l border-dashed border-slate-800/80"></div>
                  <div className="absolute top-1/2 left-0 right-0 border-t border-dashed border-slate-800/80"></div>

                  {/* Quadrant Watermark Labels */}
                  <span className="absolute top-2 left-2 text-[10px] text-slate-600 font-bold uppercase">Commercial Stronghold (High Patent / Low Research)</span>
                  <span className="absolute top-2 right-2 text-[10px] text-slate-600 font-bold uppercase">Crowded Frontier (High Patent / High Research)</span>
                  <span className="absolute bottom-2 left-2 text-[10px] text-slate-600 font-bold uppercase">Nascent Space (Low Patent / Low Research)</span>
                  <span className="absolute bottom-2 right-2 text-[10px] text-rose-500/80 font-bold uppercase">⭐ PRIME WHITESPACE (High Research / Low Patent)</span>

                  {/* Plotted Technology Bubbles */}
                  {whitespaceData?.candidates.map((ws, i) => {
                    const xPercent = Math.max(10, Math.min(90, (ws.publication_count ?? 1) * 35));
                    const yPercent = Math.max(10, Math.min(90, 100 - ((ws.patent_count ?? 0) * 35)));
                    const isHighWhitespace = (ws.whitespace_score ?? 0) >= 65;

                    return (
                      <div
                        key={ws.technology_area}
                        className={`absolute -translate-x-1/2 -translate-y-1/2 p-2 rounded-xl border cursor-pointer transition transform hover:scale-110 shadow-lg ${
                          isHighWhitespace
                            ? 'bg-rose-500/20 border-rose-500/50 text-rose-300 ring-2 ring-rose-500/20'
                            : 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                        }`}
                        style={{ left: `${xPercent}%`, top: `${yPercent}%` }}
                        title={`${ws.technology_area}: ${ws.publication_count ?? 0} Pubs vs ${ws.patent_count ?? 0} Patents`}
                      >
                        <div className="flex items-center gap-1.5 whitespace-nowrap">
                          <span className={`w-2 h-2 rounded-full ${isHighWhitespace ? 'bg-rose-400 animate-pulse' : 'bg-indigo-400'}`}></span>
                          <span className="text-[11px] font-bold">{ws.technology_area}</span>
                          <span className="text-[9px] px-1 py-0.2 rounded bg-black/40 font-mono">
                            R2P: {(ws.patent_count ?? 0) === 0 ? 'No patents (∞)' : ws.research_to_patent_ratio != null ? `${ws.research_to_patent_ratio.toFixed(1)}x` : 'N/A'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Whitespace Cards Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {whitespaceData?.candidates.map((ws) => (
                  <div
                    key={ws.technology_area}
                    className="bg-slate-900/70 border border-slate-800/90 hover:border-amber-500/50 p-5 rounded-2xl transition duration-200 space-y-4 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                            {ws.whitespace_type}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                            Confidence: {ws.confidence}
                          </span>
                        </div>
                        <h3 className="text-base font-bold text-white mt-1">{ws.technology_area}</h3>
                      </div>
                      <div className="text-right">
                        <span className="text-2xl font-black text-rose-400 block">{ws.whitespace_score.toFixed(1)}</span>
                        <span className="text-[10px] text-slate-400">Whitespace Score / 100</span>
                      </div>
                    </div>

                    {/* Research vs Patent Comparison Box */}
                    <div className="grid grid-cols-3 gap-2 bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-center">
                      <div>
                        <span className="text-[10px] text-slate-400 block">Publications (M3)</span>
                        <span className="text-sm font-bold text-cyan-400 mt-0.5 block">{ws.publication_count ?? 0}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">Patents (M5)</span>
                        <span className="text-sm font-bold text-indigo-400 mt-0.5 block">{ws.patent_count ?? 0}</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-400 block">R2P Ratio</span>
                        <span className="text-sm font-bold text-amber-400 mt-0.5 block">
                          {(ws.patent_count ?? 0) === 0 ? 'No patents (∞)' : ws.research_to_patent_ratio != null ? `${ws.research_to_patent_ratio.toFixed(1)}x` : 'N/A'}
                        </span>
                      </div>
                    </div>

                    {ws.patent_status_note && (
                      <div className="text-[11px] px-3 py-1.5 rounded-lg bg-amber-500/10 text-amber-300 border border-amber-500/20 flex items-center gap-1.5">
                        <span>ℹ️</span>
                        <span>{ws.patent_status_note}</span>
                      </div>
                    )}

                    {/* Evidence Points */}
                    <div className="space-y-1">
                      <span className="text-[10px] font-bold uppercase text-slate-400">Evidence & Findings</span>
                      <ul className="space-y-1">
                        {ws.evidence.map((ev, idx) => (
                          <li key={idx} className="text-[11px] text-slate-300 flex items-start gap-1.5">
                            <span className="text-rose-400 mt-0.5">•</span>
                            <span>{ev}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Disclaimer */}
                    <p className="text-[10px] text-slate-500 italic bg-slate-950/30 p-2 rounded-lg border border-slate-900">
                      {ws.methodology_disclaimer}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: GROWTH & VELOCITY (WITH CAGR) */}
          {activeTab === 'growth' && (
            <div className="space-y-4">
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                  <h3 className="text-sm font-bold text-white">Technological Growth Trajectories & Compound Annual Growth Rate</h3>
                  <span className="text-xs text-slate-400">Multi-Year Trajectory Analysis</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                      <tr>
                        <th className="p-3">Technology Domain</th>
                        <th className="p-3">Recent Filings</th>
                        <th className="p-3">Historical Filings</th>
                        <th className="p-3">Velocity Score</th>
                        <th className="p-3">Multi-Year CAGR</th>
                        <th className="p-3">Growth Trajectory</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-200">
                      {growthData?.items.map((g) => (
                        <tr key={g.technology_domain} className="hover:bg-slate-800/40 transition">
                          <td className="p-3 font-semibold text-white">{g.technology_domain}</td>
                          <td className="p-3 font-mono">{g.recent_period_filings}</td>
                          <td className="p-3 font-mono">{g.historical_period_filings}</td>
                          <td className="p-3 font-mono text-cyan-400">{g.velocity_score.toFixed(1)}%</td>
                          <td className="p-3 font-mono">
                            {g.cagr_pct !== null && g.cagr_pct !== undefined ? (
                              <span className="text-emerald-400 font-bold">+{g.cagr_pct.toFixed(1)}%</span>
                            ) : (
                              <span className="text-slate-500 italic">{g.cagr_status || 'Insufficient Data'}</span>
                            )}
                          </td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                              {g.growth_trajectory}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: COMPETITIVE TECHNOLOGY MONITORING (HHI) */}
          {activeTab === 'competitive' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {competitiveData?.items.map((c) => (
                  <div key={c.technology_domain} className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.concentration_tier === 'HIGHLY_CONCENTRATED'
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            : c.concentration_tier === 'MODERATELY_CONCENTRATED'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                          {c.concentration_tier}
                        </span>
                        <h3 className="text-base font-bold text-white mt-1">{c.technology_domain}</h3>
                      </div>
                      <div className="text-right">
                        <span className="text-xl font-bold text-cyan-400 block">{c.assignee_concentration_hhi.toFixed(1)}</span>
                        <span className="text-[10px] text-slate-400">Assignee HHI</span>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2">
                      <span className="text-[11px] font-bold text-slate-300 block">Leading Assignees in Field</span>
                      {c.top_assignees.map((ass) => (
                        <div key={ass.assignee} className="flex justify-between text-xs text-slate-300">
                          <span>{ass.assignee}</span>
                          <span className="font-mono text-indigo-400">{ass.patent_count} patent(s) ({ass.share_pct}%)</span>
                        </div>
                      ))}
                    </div>

                    <div className="flex justify-between text-[11px] text-slate-400">
                      <span>Composite Index: <b className="text-white">{c.composite_competitive_index}</b></span>
                      <span>Jurisdictions: {c.dominant_jurisdictions.join(', ') || 'Global'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: ADOPTION TRACKING (SEPARATE FROM R&D) */}
          {activeTab === 'adoption' && (
            <div className="space-y-4">
              <div className="bg-amber-500/10 border border-amber-500/20 p-5 rounded-2xl text-xs text-amber-300 space-y-2">
                <div className="flex items-center gap-2 font-bold text-sm text-white">
                  <span>⚠️</span>
                  <span>Strict Separation of Technology Adoption vs. R&D Publications / IP Disclosures</span>
                </div>
                <p className="leading-relaxed">
                  Per mentor specifications, high research publications and patent disclosures represent scientific and intellectual property momentum, not guaranteed enterprise adoption. In the absence of direct market sales and enterprise deployment data, adoption status is explicitly classified as <b className="text-white">DATA_UNAVAILABLE</b>.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {adoptionData?.items.map((ad) => (
                  <div key={ad.technology_domain} className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="px-2.5 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-300">
                        {ad.adoption_status}
                      </span>
                      <span className="text-xs text-slate-400">Commercial Evidence: None</span>
                    </div>
                    <h3 className="text-base font-bold text-white">{ad.technology_domain}</h3>
                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <div>
                        <span className="text-slate-400 block text-[10px]">Research Momentum</span>
                        <span className="font-semibold text-cyan-400">{ad.research_activity_level}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px]">Patent Disclosures</span>
                        <span className="font-semibold text-indigo-400">{ad.patent_activity_level}</span>
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed italic">{ad.notes}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
