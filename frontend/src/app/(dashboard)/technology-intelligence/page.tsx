'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  TechnologyIntelligenceSummary,
  TechnologyActivityResponse,
  TechnologyGrowthResponse,
  TechnologyCoverageResponse,
  WhitespaceDiscoveryResponse,
} from '@/types/technology_intelligence';

export default function TechnologyIntelligencePage() {
  const [activeTab, setActiveTab] = useState<'whitespace' | 'activity' | 'growth' | 'coverage'>('whitespace');
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [whitespaceThreshold, setWhitespaceThreshold] = useState(45);

  const [summary, setSummary] = useState<TechnologyIntelligenceSummary | null>(null);
  const [activityData, setActivityData] = useState<TechnologyActivityResponse | null>(null);
  const [growthData, setGrowthData] = useState<TechnologyGrowthResponse | null>(null);
  const [coverageData, setCoverageData] = useState<TechnologyCoverageResponse | null>(null);
  const [whitespaceData, setWhitespaceData] = useState<WhitespaceDiscoveryResponse | null>(null);

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

      const [sumRes, actRes, grRes, covRes, wsRes] = await Promise.all([
        api.get<{ data: TechnologyIntelligenceSummary }>(`/api/v1/technology-intelligence/summary${queryStr}`),
        api.get<{ data: TechnologyActivityResponse }>(`/api/v1/technology-intelligence/activity${queryStr}`),
        api.get<{ data: TechnologyGrowthResponse }>(`/api/v1/technology-intelligence/growth${queryStr}`),
        api.get<{ data: TechnologyCoverageResponse }>(`/api/v1/technology-intelligence/coverage${queryStr}`),
        api.get<{ data: WhitespaceDiscoveryResponse }>(`/api/v1/technology-intelligence/whitespace${queryStr}`),
      ]);

      setSummary(sumRes.data.data);
      setActivityData(actRes.data.data);
      setGrowthData(grRes.data.data);
      setCoverageData(covRes.data.data);
      setWhitespaceData(wsRes.data.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load technology intelligence');
    } finally {
      setLoading(false);
    }
  }, [myProfileOnly, selectedDomain, whitespaceThreshold]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Technology Intelligence
            </span>
            <span className="text-xs text-slate-400">
              Indexed Corpus: {summary?.total_patents ?? 0} Patents across {summary?.total_technology_areas ?? 0} Fields
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Technology Intelligence & Whitespace Discovery</h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Deterministic patent gap detection, technological growth velocity, and multi-signal coverage density across global and portfolio IP datasets.
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
            {myProfileOnly ? 'My Profile Scoped' : 'Global Patent Corpus'}
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
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Total Patents</span>
          <span className="text-xl font-bold text-white mt-1 block">
            {summary?.total_patents ?? 0}
          </span>
          <span className="text-[10px] text-cyan-400">Indexed Corpus</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Active Fields</span>
          <span className="text-xl font-bold text-indigo-400 mt-1 block">
            {summary?.active_areas_count ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">High / Medium Activity</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Growing Fields</span>
          <span className="text-xl font-bold text-emerald-400 mt-1 block">
            {summary?.growing_areas_count ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">Positive Velocity</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Potential Whitespaces</span>
          <span className="text-xl font-bold text-amber-400 mt-1 block">
            {summary?.potential_whitespaces_count ?? 0}
          </span>
          <span className="text-[10px] text-slate-400">Gaps Identified</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 col-span-2 md:col-span-1">
          <span className="text-[11px] text-slate-400 font-medium block">Threshold Used</span>
          <span className="text-xl font-bold text-rose-400 mt-1 block">
            {whitespaceThreshold} / 100
          </span>
          <span className="text-[10px] text-slate-400">Sensitivity Score</span>
        </div>
      </div>

      {/* Filter and Tab Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl space-y-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 overflow-x-auto max-w-full">
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
              onClick={() => setActiveTab('activity')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'activity' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Technology Activity ({activityData?.items?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('growth')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'growth' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Growth & Velocity ({growthData?.items?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('coverage')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition whitespace-nowrap ${
                activeTab === 'coverage' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Coverage Density ({coverageData?.items?.length ?? 0})
            </button>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Technology Domains</option>
              {activityData?.items?.map((item) => (
                <option key={item.technology_domain} value={item.technology_domain}>
                  {item.technology_domain}
                </option>
              ))}
            </select>

            <div className="flex items-center gap-2">
              <span className="text-[10px] text-slate-400 whitespace-nowrap">Threshold: {whitespaceThreshold}</span>
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
          {/* TAB 1: WHITESPACE DISCOVERY */}
          {activeTab === 'whitespace' && (
            <div className="space-y-4">
              {whitespaceData?.candidates.length === 0 ? (
                <div className="text-center py-16 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8">
                  <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
                    🔍
                  </div>
                  <h3 className="text-base font-semibold text-slate-200">No Potential Whitespaces Detected</h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                    Try lowering the sensitivity threshold slider or expanding your technology domain filters.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {whitespaceData?.candidates.map((ws) => (
                    <div
                      key={ws.technology_area}
                      className="bg-slate-900/70 border border-slate-800/90 hover:border-amber-500/50 p-5 rounded-2xl transition duration-200 space-y-4 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              ws.whitespace_type === 'POTENTIAL_WHITESPACE'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : ws.whitespace_type === 'ACTIVITY_GAP'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                            }`}>
                              {ws.whitespace_type.replace(/_/g, ' ')}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                              Confidence: <strong className="text-white">{ws.confidence}</strong>
                            </span>
                          </div>
                          <h3 className="text-base font-bold text-white mt-1.5">{ws.technology_area}</h3>
                        </div>

                        <div className="text-right">
                          <span className="text-2xl font-extrabold text-amber-400">{ws.whitespace_score}</span>
                          <span className="text-[10px] text-slate-500 block">Gap Score / 100</span>
                        </div>
                      </div>

                      {/* 4 Gap Sub-scores */}
                      <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-800/80 text-center text-xs">
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/60">
                          <span className="text-[10px] text-slate-400 block">Volume Gap</span>
                          <span className="font-bold text-slate-200">{ws.activity_gap_score}</span>
                        </div>
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/60">
                          <span className="text-[10px] text-slate-400 block">Assignee Gap</span>
                          <span className="font-bold text-slate-200">{ws.assignee_gap_score}</span>
                        </div>
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/60">
                          <span className="text-[10px] text-slate-400 block">Recency Gap</span>
                          <span className="font-bold text-slate-200">{ws.growth_gap_score}</span>
                        </div>
                        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/60">
                          <span className="text-[10px] text-slate-400 block">Coverage Gap</span>
                          <span className="font-bold text-slate-200">{ws.coverage_gap_score}</span>
                        </div>
                      </div>

                      {/* Evidence List */}
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-semibold text-slate-300 block">Supporting Empirical Evidence:</span>
                        <ul className="space-y-1">
                          {ws.evidence.map((ev, idx) => (
                            <li key={idx} className="text-xs text-slate-400 flex items-start gap-1.5">
                              <span className="text-amber-400 text-[10px] mt-0.5">•</span>
                              <span>{ev}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Adjacent Technology Context */}
                      {ws.adjacent_technology_areas && ws.adjacent_technology_areas.length > 0 && (
                        <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2 text-[10px] text-slate-400">
                          <span>Adjacent Active Fields:</span>
                          <span className="text-slate-300 font-medium">{ws.adjacent_technology_areas.join(', ')}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: TECHNOLOGY ACTIVITY */}
          {activeTab === 'activity' && (
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Technology Activity Distribution</h3>
                <span className="text-xs text-slate-400 font-mono">
                  {activityData?.items?.length ?? 0} Fields Analyzed
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Technology Area / Domain</th>
                      <th className="pb-2 font-medium">Patents</th>
                      <th className="pb-2 font-medium">Recent (24mo)</th>
                      <th className="pb-2 font-medium">Grants</th>
                      <th className="pb-2 font-medium">Avg Citations</th>
                      <th className="pb-2 font-medium">Assignees</th>
                      <th className="pb-2 font-medium">Jurisdictions</th>
                      <th className="pb-2 font-medium">Activity Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {activityData?.items?.map((item) => (
                      <tr key={item.technology_area} className="hover:bg-slate-950/40">
                        <td className="py-2.5 font-semibold text-slate-200">{item.technology_area}</td>
                        <td className="py-2.5 text-slate-300">{item.patent_count}</td>
                        <td className="py-2.5 text-cyan-400 font-medium">{item.recent_patent_count}</td>
                        <td className="py-2.5 text-slate-300">{item.grant_count}</td>
                        <td className="py-2.5 text-amber-400">{item.average_citations}</td>
                        <td className="py-2.5 text-slate-300">{item.assignee_count}</td>
                        <td className="py-2.5 text-slate-400 font-mono text-[10px]">{item.jurisdictions.join(', ') || 'Global'}</td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            item.activity_level === 'HIGH_ACTIVITY'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : item.activity_level === 'MEDIUM_ACTIVITY'
                              ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          }`}>
                            {item.activity_level.replace(/_/g, ' ')}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 3: GROWTH & VELOCITY */}
          {activeTab === 'growth' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {growthData?.items?.map((g) => (
                <div key={g.technology_area} className="bg-slate-900/70 border border-slate-800 p-5 rounded-2xl space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h4 className="text-sm font-bold text-white">{g.technology_area}</h4>
                      <span className="text-[10px] text-slate-400">{g.technology_domain}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      g.growth_trajectory === 'RAPID_ACCELERATION'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : g.growth_trajectory === 'STEADY_GROWTH'
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                        : g.growth_trajectory === 'MATURE_STABLE'
                        ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                        : 'bg-slate-800 text-slate-400'
                    }`}>
                      {g.growth_trajectory.replace(/_/g, ' ')}
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">Recent Velocity:</span>
                      <span className="font-bold text-cyan-400">{g.velocity_score}%</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        style={{ width: `${Math.min(100, Math.max(5, g.velocity_score))}%` }}
                        className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800/80">
                    <div>
                      <span className="text-[10px] text-slate-500 block">Recent Filings:</span>
                      <span className="font-semibold text-slate-200">{g.recent_period_filings}</span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block">Historical Filings:</span>
                      <span className="font-semibold text-slate-200">{g.historical_period_filings}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: COVERAGE DENSITY */}
          {activeTab === 'coverage' && (
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">Multi-Signal Coverage Density</h3>
                <span className="text-xs text-slate-400 font-mono">
                  {coverageData?.items?.length ?? 0} Fields Evaluated
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="pb-2 font-medium">Technology Area</th>
                      <th className="pb-2 font-medium">Patents</th>
                      <th className="pb-2 font-medium">Assignees</th>
                      <th className="pb-2 font-medium">Jurisdictions</th>
                      <th className="pb-2 font-medium">Coverage Density Score</th>
                      <th className="pb-2 font-medium">Coverage Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {coverageData?.items?.map((item) => (
                      <tr key={item.technology_area} className="hover:bg-slate-950/40">
                        <td className="py-2.5 font-semibold text-slate-200">{item.technology_area}</td>
                        <td className="py-2.5 text-slate-300">{item.patent_count}</td>
                        <td className="py-2.5 text-slate-300">{item.assignee_count}</td>
                        <td className="py-2.5 text-slate-300">{item.jurisdiction_count}</td>
                        <td className="py-2.5">
                          <span className="font-bold text-indigo-400">{item.coverage_density_score} / 100</span>
                        </td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            item.coverage_level === 'HIGH_COVERAGE'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : item.coverage_level === 'MODERATE_COVERAGE'
                              ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          }`}>
                            {item.coverage_level.replace(/_/g, ' ')}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Methodology Disclaimer Banner */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-400 text-xs leading-relaxed space-y-1">
        <p className="font-semibold text-slate-300 flex items-center gap-1.5">
          <span>ℹ️</span> Methodology & Governance Notice
        </p>
        <p>
          Technology Intelligence metrics, Growth Trajectories, and Whitespace Gap Indicators are empirical metadata aggregations derived from indexed patent records. A detected potential whitespace does not constitute an assessment of legal patentability, freedom-to-operate, or guaranteed commercial opportunity.
        </p>
      </div>
    </div>
  );
}
