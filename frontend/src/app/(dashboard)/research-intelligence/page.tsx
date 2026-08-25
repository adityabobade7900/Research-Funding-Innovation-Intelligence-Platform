"use client";

import React, { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  TrendingUp,
  BarChart3,
  Flame,
  Zap,
  BookOpen,
  Award,
  Sparkles,
  Search,
  Filter,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
  ExternalLink,
  ShieldCheck,
  Globe2,
  UserCheck,
  Calendar,
  Layers,
  ChevronRight,
  Target,
  AlertCircle
} from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  PublicationTrendsResponse,
  DomainTrendsResponse,
  KeywordTrendsResponse,
  CitationStatisticsResponse,
  EmergingTopicsResponse,
  ResearchHotspotsResponse
} from "@/types/research_intelligence";
import { FundingRecommendationResponse } from "@/types/funding";

export default function ResearchIntelligenceDashboard() {
  // Global Filter State
  const [myProfileOnly, setMyProfileOnly] = useState<boolean>(false);
  const [startYear, setStartYear] = useState<string>("");
  const [endYear, setEndYear] = useState<string>("");
  const [selectedDomain, setSelectedDomain] = useState<string>("");
  const [keywordQuery, setKeywordQuery] = useState<string>("");

  // Loading & Error States
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "trends" | "hotspots" | "emerging" | "citations">("overview");

  // Data States
  const [pubTrends, setPubTrends] = useState<PublicationTrendsResponse | null>(null);
  const [domainTrends, setDomainTrends] = useState<DomainTrendsResponse | null>(null);
  const [keywordTrends, setKeywordTrends] = useState<KeywordTrendsResponse | null>(null);
  const [citationStats, setCitationStats] = useState<CitationStatisticsResponse | null>(null);
  const [emergingTopics, setEmergingTopics] = useState<EmergingTopicsResponse | null>(null);
  const [hotspots, setHotspots] = useState<ResearchHotspotsResponse | null>(null);
  const [fundingRecs, setFundingRecs] = useState<FundingRecommendationResponse | null>(null);

  // Fetch all analytics datasets
  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const queryParams: Record<string, any> = {
        my_profile_only: myProfileOnly,
      };
      if (startYear) queryParams.start_year = parseInt(startYear, 10);
      if (endYear) queryParams.end_year = parseInt(endYear, 10);
      if (selectedDomain) queryParams.domain = selectedDomain;
      if (keywordQuery) queryParams.keyword = keywordQuery;

      const [pubRes, domRes, kwRes, citRes, emRes, hotRes, recRes] = await Promise.allSettled([
        api.get("/research-intelligence/trends/publications", { params: queryParams }),
        api.get("/research-intelligence/trends/domains", { params: queryParams }),
        api.get("/research-intelligence/trends/keywords", { params: { ...queryParams, limit: 20, min_count: 1 } }),
        api.get("/research-intelligence/trends/citations", { params: queryParams }),
        api.get("/research-intelligence/emerging-topics", { params: { ...queryParams, recent_years: 2, min_count: 1 } }),
        api.get("/research-intelligence/hotspots", { params: { recent_years: 2, my_profile_only: myProfileOnly } }),
        api.get("/funding/recommendations", { params: { limit: 3, minimum_score: 50 } })
      ]);

      if (pubRes.status === "fulfilled" && pubRes.value.data.success) {
        setPubTrends(pubRes.value.data.data);
      }
      if (domRes.status === "fulfilled" && domRes.value.data.success) {
        setDomainTrends(domRes.value.data.data);
      }
      if (kwRes.status === "fulfilled" && kwRes.value.data.success) {
        setKeywordTrends(kwRes.value.data.data);
      }
      if (citRes.status === "fulfilled" && citRes.value.data.success) {
        setCitationStats(citRes.value.data.data);
      }
      if (emRes.status === "fulfilled" && emRes.value.data.success) {
        setEmergingTopics(emRes.value.data.data);
      }
      if (hotRes.status === "fulfilled" && hotRes.value.data.success) {
        setHotspots(hotRes.value.data.data);
      }
      if (recRes.status === "fulfilled" && recRes.value.data.success) {
        setFundingRecs(recRes.value.data.data);
      }
    } catch (err: any) {
      console.error("Failed to load research intelligence:", err);
      setError("Unable to compute research intelligence metrics. Please verify network connectivity.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [myProfileOnly, startYear, endYear, selectedDomain]);

  // Handle Keyword Filter Submission
  const handleKeywordSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchDashboardData();
  };

  const handleResetFilters = () => {
    setStartYear("");
    setEndYear("");
    setSelectedDomain("");
    setKeywordQuery("");
  };

  // Max publication count in yearly trends for SVG scaling
  const maxPubCount = useMemo(() => {
    if (!pubTrends?.points?.length) return 10;
    return Math.max(...pubTrends.points.map((p) => p.publication_count), 5);
  }, [pubTrends]);

  // Max citations in yearly breakdown for SVG scaling
  const maxCitationYearCount = useMemo(() => {
    if (!citationStats?.citations_by_year?.length) return 10;
    return Math.max(...citationStats.citations_by_year.map((c) => c.total_citations), 5);
  }, [citationStats]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-blue-950/40 to-slate-900 border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="space-y-1.5 z-10">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Research Intelligence & Trend Analytics
            </h1>
            <Badge variant="primary" className="ml-2 bg-blue-500/10 text-blue-400 border-blue-500/30">
              M2F Statistical Engine
            </Badge>
          </div>
          <p className="text-xs text-slate-400 max-w-2xl">
            Data-driven scientific publication trajectories, domain market shares, statistical topic velocity,
            and deterministic hotspot discovery across your portfolio and the global ecosystem.
          </p>
        </div>

        {/* Scope Toggle & Refresh */}
        <div className="flex items-center gap-3 z-10">
          <div className="inline-flex p-1 rounded-xl bg-slate-950/80 border border-slate-800">
            <button
              onClick={() => setMyProfileOnly(false)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                !myProfileOnly
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Globe2 className="w-3.5 h-3.5" />
              Global Corpus
            </button>
            <button
              onClick={() => setMyProfileOnly(true)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                myProfileOnly
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" />
              My Portfolio
            </button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={fetchDashboardData}
            disabled={isLoading}
            className="border-slate-800 bg-slate-900/80 text-slate-300 hover:text-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-blue-400" : ""}`} />
          </Button>
        </div>
      </div>

      {/* Filter Control Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-wrap items-center gap-3 text-xs">
        <div className="flex items-center gap-1.5 text-slate-400 font-semibold mr-1">
          <Filter className="w-3.5 h-3.5 text-blue-400" />
          <span>Filters:</span>
        </div>

        {/* Start Year */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">From:</span>
          <select
            value={startYear}
            onChange={(e) => setStartYear(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">Min Year</option>
            <option value="2020">2020</option>
            <option value="2021">2021</option>
            <option value="2022">2022</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
            <option value="2026">2026</option>
          </select>
        </div>

        {/* End Year */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">To:</span>
          <select
            value={endYear}
            onChange={(e) => setEndYear(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">Max Year</option>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
            <option value="2026">2026</option>
          </select>
        </div>

        {/* Domain Selector */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500">Domain:</span>
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-blue-500 max-w-[200px] truncate"
          >
            <option value="">All Research Domains</option>
            {domainTrends?.domains?.map((d) => (
              <option key={d.domain} value={d.domain}>
                {d.domain}
              </option>
            ))}
          </select>
        </div>

        {/* Keyword Search Form */}
        <form onSubmit={handleKeywordSearch} className="flex items-center gap-1.5 flex-1 min-w-[200px]">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter keyword/topic..."
              value={keywordQuery}
              onChange={(e) => setKeywordQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>
          <Button type="submit" size="sm" variant="secondary" className="px-2.5 py-1.5">
            Search
          </Button>
        </form>

        {(startYear || endYear || selectedDomain || keywordQuery) && (
          <button
            onClick={handleResetFilters}
            className="text-xs text-rose-400 hover:text-rose-300 transition-colors ml-auto underline"
          >
            Reset Filters
          </button>
        )}
      </div>

      {/* Top KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Publications */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Publications</span>
            <BookOpen className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-white">
              {isLoading ? "..." : pubTrends?.total_publications ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              {pubTrends?.year_range?.min_year && pubTrends?.year_range?.max_year
                ? `${pubTrends.year_range.min_year} – ${pubTrends.year_range.max_year}`
                : "Indexed papers"}
            </p>
          </div>
        </div>

        {/* Total Citations */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Total Citations</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-300">
              {isLoading ? "..." : citationStats?.total_citations ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              Avg {citationStats?.average_citations ?? 0} / paper
            </p>
          </div>
        </div>

        {/* Median Citations */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Median Citations</span>
            <BarChart3 className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-300">
              {isLoading ? "..." : citationStats?.median_citations ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">
              Max {citationStats?.max_citations ?? 0} citations
            </p>
          </div>
        </div>

        {/* Active Hotspots */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Research Hotspots</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-rose-400">
              {isLoading ? "..." : hotspots?.total_hotspots ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">High-activity clusters</p>
          </div>
        </div>

        {/* Emerging Topics */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Emerging Topics</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-cyan-300">
              {isLoading ? "..." : emergingTopics?.total_emerging ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Accelerating velocity</p>
          </div>
        </div>

        {/* Top Matched Funding */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Funding Matches</span>
            <Target className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-300">
              {isLoading ? "..." : fundingRecs?.total_recommended ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Personalized RFPs</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === "overview"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Intelligence Overview
        </button>
        <button
          onClick={() => setActiveTab("trends")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === "trends"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Publication & Domain Trends
        </button>
        <button
          onClick={() => setActiveTab("emerging")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === "emerging"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Emerging Topics Velocity
        </button>
        <button
          onClick={() => setActiveTab("hotspots")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === "hotspots"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Research Hotspots
        </button>
        <button
          onClick={() => setActiveTab("citations")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            activeTab === "citations"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Citation Impact & Top Papers
        </button>
      </div>

      {/* TAB 1: Intelligence Overview / Combined Visuals */}
      {(activeTab === "overview" || activeTab === "trends") && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chart: Publication Volume by Year */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-blue-400" />
                  Publication Trajectory & YoY Growth
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Year-over-Year publication output and velocity rate
                </p>
              </div>
              <Badge variant="secondary" className="text-slate-300 border-slate-700">
                {pubTrends?.points?.length ?? 0} Active Years
              </Badge>
            </div>

            {/* Custom Responsive SVG Chart */}
            {pubTrends?.points && pubTrends.points.length > 0 ? (
              <div className="space-y-4">
                <div className="h-64 flex items-end justify-between gap-4 pt-8 pb-2 border-b border-slate-800 px-4">
                  {pubTrends.points.map((pt) => {
                    const heightPercent = Math.max(12, Math.round((pt.publication_count / maxPubCount) * 100));
                    return (
                      <div key={pt.year} className="flex-1 flex flex-col items-center gap-2 group relative">
                        {/* Hover Tooltip */}
                        <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-700 rounded-lg p-2 text-center text-[10px] pointer-events-none z-20 shadow-xl min-w-[100px]">
                          <span className="font-bold text-white block">{pt.year}: {pt.publication_count} papers</span>
                          {pt.growth_rate !== null && (
                            <span className={pt.growth_rate >= 0 ? "text-emerald-400" : "text-rose-400"}>
                              {pt.growth_rate >= 0 ? `+${pt.growth_rate}%` : `${pt.growth_rate}%`} YoY
                            </span>
                          )}
                        </div>

                        {/* YoY Growth Badge */}
                        {pt.growth_rate !== null ? (
                          <div className={`text-[10px] font-semibold flex items-center ${
                            pt.growth_rate >= 0 ? "text-emerald-400" : "text-rose-400"
                          }`}>
                            {pt.growth_rate >= 0 ? (
                              <ArrowUpRight className="w-3 h-3 inline mr-0.5" />
                            ) : (
                              <ArrowDownRight className="w-3 h-3 inline mr-0.5" />
                            )}
                            {pt.growth_rate}%
                          </div>
                        ) : (
                          <span className="text-[10px] text-slate-500">Base</span>
                        )}

                        {/* Bar */}
                        <div
                          style={{ height: `${heightPercent}%` }}
                          className="w-full max-w-[56px] rounded-t-xl bg-gradient-to-t from-blue-600 to-cyan-400 shadow-md shadow-blue-500/20 group-hover:from-blue-500 group-hover:to-cyan-300 transition-all cursor-pointer flex items-end justify-center pb-2"
                        >
                          <span className="text-[10px] font-bold text-white drop-shadow">
                            {pt.publication_count}
                          </span>
                        </div>

                        {/* Year Label */}
                        <span className="text-xs font-semibold text-slate-300 mt-1">
                          {pt.year}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="flex items-center justify-between text-xs text-slate-400 px-2">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded bg-blue-500 inline-block"></span>
                    <span>Publication Volume</span>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400">
                    <ArrowUpRight className="w-3.5 h-3.5" />
                    <span>YoY Growth Rate</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-xs">
                <BookOpen className="w-8 h-8 text-slate-600 mb-2" />
                No publications found for the selected filter range.
              </div>
            )}
          </div>

          {/* Research Domain Distribution Leaderboard */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Domain Market Share
              </h3>
              <Badge variant="purple" className="text-purple-400 border-purple-500/30">
                {domainTrends?.domains?.length ?? 0} Domains
              </Badge>
            </div>

            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
              {domainTrends?.domains && domainTrends.domains.length > 0 ? (
                domainTrends.domains.map((dom) => {
                  const latestPoint = dom.yearly_distribution[dom.yearly_distribution.length - 1];
                  const share = latestPoint ? latestPoint.share_percentage : 0;
                  return (
                    <div
                      key={dom.domain}
                      className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-purple-500/30 transition-all space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-slate-200 truncate max-w-[180px]">
                          {dom.domain}
                        </span>
                        <span className="font-bold text-purple-300">{dom.total_publications} papers</span>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          style={{ width: `${Math.min(100, Math.max(8, share))}%` }}
                          className="h-full bg-gradient-to-r from-purple-600 to-indigo-500 rounded-full"
                        ></div>
                      </div>

                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span>Latest Share: {share}%</span>
                        <span>Avg Citations: {dom.average_citations}</span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No domain distribution data available.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2 & OVERVIEW: Emerging Topics & Research Hotspots */}
      {(activeTab === "overview" || activeTab === "emerging" || activeTab === "hotspots") && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Emerging Topics Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-cyan-400" />
                  Emerging Topics Velocity
                </h3>
                <p className="text-[11px] text-slate-400">
                  Statistical velocity model comparing recent window vs historical baseline
                </p>
              </div>
              <Badge variant="secondary" className="text-cyan-400 border-cyan-500/30">
                Top {emergingTopics?.topics?.length ?? 0}
              </Badge>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {emergingTopics?.topics && emergingTopics.topics.length > 0 ? (
                emergingTopics.topics.map((topic, idx) => (
                  <div
                    key={topic.topic}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/30 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-[10px] font-bold text-cyan-400 flex items-center justify-center">
                          #{idx + 1}
                        </span>
                        <span className="text-xs font-bold text-white">{topic.topic}</span>
                      </div>

                      <Badge
                        variant={
                          topic.status === "EMERGING"
                            ? "success"
                            : topic.status === "ESTABLISHED_GROWING"
                            ? "primary"
                            : "secondary"
                        }
                        className="text-[10px]"
                      >
                        {topic.status}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-3 gap-2 py-1 bg-slate-900/40 rounded-lg p-2 text-center text-[11px]">
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase">Recent (2Y)</span>
                        <span className="font-bold text-cyan-300">{topic.recent_count}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase">Historical</span>
                        <span className="font-bold text-slate-300">{topic.historical_count}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[9px] uppercase">Velocity Score</span>
                        <span className="font-bold text-emerald-400">{topic.velocity_score} / 10</span>
                      </div>
                    </div>

                    {topic.reasons && topic.reasons.length > 0 && (
                      <p className="text-[10px] text-slate-400 italic">
                        • {topic.reasons[0]}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">
                  No emerging topics detected with current threshold.
                </div>
              )}
            </div>
          </div>

          {/* Research Hotspots Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Flame className="w-4 h-4 text-rose-400" />
                  Research Hotspots
                </h3>
                <p className="text-[11px] text-slate-400">
                  Composite intensity combining publication volume, growth rate, and citation impact
                </p>
              </div>
              <Badge variant="secondary" className="text-rose-400 border-rose-500/30">
                {hotspots?.hotspots?.length ?? 0} Clusters
              </Badge>
            </div>

            <div className="space-y-3 max-h-[380px] overflow-y-auto pr-1">
              {hotspots?.hotspots && hotspots.hotspots.length > 0 ? (
                hotspots.hotspots.map((h, idx) => (
                  <div
                    key={h.domain_or_topic}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-rose-500/30 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-[10px] font-bold text-rose-400 flex items-center justify-center">
                          #{idx + 1}
                        </span>
                        <span className="text-xs font-bold text-white truncate max-w-[200px]">
                          {h.domain_or_topic}
                        </span>
                      </div>

                      <Badge
                        variant={
                          h.classification === "CRITICAL_HOTSPOT"
                            ? "danger"
                            : h.classification === "HIGH_ACTIVITY"
                            ? "warning"
                            : "secondary"
                        }
                        className="text-[10px]"
                      >
                        {h.classification.replace("_", " ")}
                      </Badge>
                    </div>

                    {/* Hotspot Intensity Meter */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[10px]">
                        <span className="text-slate-400">Hotspot Intensity Score</span>
                        <span className="font-bold text-rose-400">{h.hotspot_score} / 100</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          style={{ width: `${Math.min(100, Math.max(5, h.hotspot_score))}%` }}
                          className="h-full bg-gradient-to-r from-rose-500 to-amber-400 rounded-full"
                        ></div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-1 mt-1">
                      {h.key_drivers.map((driver, dIdx) => (
                        <span
                          key={dIdx}
                          className="text-[10px] px-2 py-0.5 rounded-md bg-slate-900 text-slate-300 border border-slate-800"
                        >
                          {driver}
                        </span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-slate-500 text-xs">
                  No active research hotspots identified.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Keyword Frequency Matrix */}
      {(activeTab === "overview" || activeTab === "trends") && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Search className="w-4 h-4 text-indigo-400" />
                Keyword & Thematic Trajectories
              </h3>
              <p className="text-xs text-slate-400">
                Top scientific keywords ranked by lifetime occurrences and recent activity
              </p>
            </div>
            <Badge variant="secondary" className="text-indigo-400 border-indigo-500/30">
              {keywordTrends?.keywords?.length ?? 0} Keywords
            </Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {keywordTrends?.keywords && keywordTrends.keywords.length > 0 ? (
              keywordTrends.keywords.map((kw) => (
                <div
                  key={kw.keyword}
                  className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-indigo-500/30 transition-all flex items-center justify-between"
                >
                  <div className="overflow-hidden">
                    <span className="text-xs font-semibold text-slate-200 block truncate">
                      {kw.keyword}
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Recent: {kw.recent_count} (2Y)
                    </span>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-xs font-bold text-indigo-400 block">
                      {kw.total_occurrences}
                    </span>
                    <span className="text-[9px] text-slate-500 uppercase">Occurrences</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-8 text-slate-500 text-xs">
                No keyword trajectories recorded for current selection.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: Citation Analytics & High-Impact Publications */}
      {(activeTab === "overview" || activeTab === "citations") && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Yearly Citation Trend Chart */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-400" />
              Citations by Publication Year
            </h3>
            <p className="text-xs text-slate-400">
              Aggregated citation volume and average citations per paper by cohort year
            </p>

            <div className="h-56 flex items-end justify-between gap-3 pt-6 pb-2 border-b border-slate-800 px-2">
              {citationStats?.citations_by_year && citationStats.citations_by_year.length > 0 ? (
                citationStats.citations_by_year.map((c) => {
                  const hPercent = Math.max(10, Math.round((c.total_citations / maxCitationYearCount) * 100));
                  return (
                    <div key={c.year} className="flex-1 flex flex-col items-center gap-1.5 group relative">
                      <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-950 border border-slate-700 rounded-lg p-1.5 text-center text-[10px] pointer-events-none z-20 shadow-xl min-w-[90px]">
                        <span className="font-bold text-white block">{c.year}: {c.total_citations} cit.</span>
                        <span className="text-amber-400">Avg {c.average_citations} / paper</span>
                      </div>

                      <span className="text-[10px] font-semibold text-amber-400">
                        {c.total_citations}
                      </span>

                      <div
                        style={{ height: `${hPercent}%` }}
                        className="w-full max-w-[40px] rounded-t-lg bg-gradient-to-t from-amber-600 to-yellow-400 group-hover:from-amber-500 group-hover:to-yellow-300 transition-all cursor-pointer"
                      ></div>

                      <span className="text-xs text-slate-300 mt-1 font-semibold">{c.year}</span>
                    </div>
                  );
                })
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                  No citation timeline data available.
                </div>
              )}
            </div>
          </div>

          {/* High-Impact Top-Cited Publications Leaderboard */}
          <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Top-Cited Publications
                </h3>
                <p className="text-xs text-slate-400">
                  Highest-impact papers in the current research corpus
                </p>
              </div>
              <Link href="/publications">
                <Button variant="outline" size="sm" className="text-xs border-slate-800">
                  View All Papers
                  <ChevronRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </Link>
            </div>

            <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
              {citationStats?.top_cited_publications && citationStats.top_cited_publications.length > 0 ? (
                citationStats.top_cited_publications.map((p, idx) => (
                  <div
                    key={p.id}
                    className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-amber-500/30 transition-all flex items-start justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-md bg-amber-500/10 border border-amber-500/30 text-[10px] font-bold text-amber-400 flex items-center justify-center">
                          #{idx + 1}
                        </span>
                        <h4 className="text-xs font-bold text-slate-100 hover:text-blue-400 transition-colors">
                          {p.title}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 pl-7">
                        {p.venue && <span>{p.venue}</span>}
                        {p.primary_domain && (
                          <Badge variant="secondary" className="text-[9px] py-0 border-slate-700">
                            {p.primary_domain}
                          </Badge>
                        )}
                        {p.doi && (
                          <span className="font-mono text-slate-500 truncate max-w-[140px]">
                            {p.doi}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="text-right flex-shrink-0">
                      <div className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 font-bold text-xs">
                        <Award className="w-3.5 h-3.5 text-amber-400" />
                        {p.citation_count}
                      </div>
                      <span className="text-[9px] text-slate-500 block mt-0.5">Citations</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-slate-500 text-xs">
                  No publications recorded in this scope.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SECTION: Funding Opportunity Recommendations Radar (M2E Integration) */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/30 via-slate-900 to-indigo-950/30 border border-blue-900/40 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-blue-400" />
              Highest-Ranked Funding Matches
            </h3>
            <p className="text-xs text-slate-400">
              Personalized grant opportunities matched to your research domains and technical keywords
            </p>
          </div>
          <Link href="/funding">
            <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-xs">
              Explore Full Funding Radar
              <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {fundingRecs?.items && fundingRecs.items.length > 0 ? (
            fundingRecs.items.slice(0, 3).map((rec, rIdx) => (
              <div
                key={rec.opportunity.id}
                className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-blue-500/40 transition-all flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge variant="primary" className="text-[10px]">
                      #{rIdx + 1} Match
                    </Badge>
                    <span className="text-xs font-bold text-emerald-400">
                      {rec.recommendation_score}% Match
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-white line-clamp-2">
                    {rec.opportunity.title}
                  </h4>

                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>{rec.opportunity.funding_agency}</span>
                    {rec.opportunity.funding_amount && (
                      <span className="font-semibold text-slate-200">
                        ${(rec.opportunity.funding_amount / 1000).toFixed(0)}k
                      </span>
                    )}
                  </div>
                </div>

                {rec.reasons && rec.reasons.length > 0 && (
                  <p className="text-[10px] text-slate-400 line-clamp-1 italic">
                    • {rec.reasons[0]}
                  </p>
                )}
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-6 text-slate-500 text-xs">
              No recommendations available. Complete your research profile to activate personalized funding matches.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
