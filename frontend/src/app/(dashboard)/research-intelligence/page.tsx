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
  AlertCircle,
  Compass,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  FileText
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
  ResearchHotspotsResponse,
  ResearchGapItem,
  ResearchGapsResponse
} from "@/types/research_intelligence";
import {
  PublicationRecommendationItem,
  PublicationRecommendationsResponse
} from "@/types/publication";
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
  const [activeTab, setActiveTab] = useState<"overview" | "trends" | "hotspots" | "emerging" | "citations" | "gaps" | "recommendations">("overview");

  // Data States
  const [pubTrends, setPubTrends] = useState<PublicationTrendsResponse | null>(null);
  const [domainTrends, setDomainTrends] = useState<DomainTrendsResponse | null>(null);
  const [keywordTrends, setKeywordTrends] = useState<KeywordTrendsResponse | null>(null);
  const [citationStats, setCitationStats] = useState<CitationStatisticsResponse | null>(null);
  const [emergingTopics, setEmergingTopics] = useState<EmergingTopicsResponse | null>(null);
  const [hotspots, setHotspots] = useState<ResearchHotspotsResponse | null>(null);
  const [fundingRecs, setFundingRecs] = useState<FundingRecommendationResponse | null>(null);
  const [researchGaps, setResearchGaps] = useState<ResearchGapsResponse | null>(null);
  const [paperRecs, setPaperRecs] = useState<PublicationRecommendationsResponse | null>(null);
  const [gapsError, setGapsError] = useState<string | null>(null);
  const [recsError, setRecsError] = useState<string | null>(null);

  // Fetch all analytics datasets
  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    setGapsError(null);
    setRecsError(null);
    try {
      const queryParams: Record<string, any> = {
        my_profile_only: myProfileOnly,
      };
      if (startYear) queryParams.start_year = parseInt(startYear, 10);
      if (endYear) queryParams.end_year = parseInt(endYear, 10);
      if (selectedDomain) queryParams.domain = selectedDomain;
      if (keywordQuery) queryParams.keyword = keywordQuery;

      const [pubRes, domRes, kwRes, citRes, emRes, hotRes, recRes, gapsRes, paperRecRes] = await Promise.allSettled([
        api.get("/research-intelligence/trends/publications", { params: queryParams }),
        api.get("/research-intelligence/trends/domains", { params: queryParams }),
        api.get("/research-intelligence/trends/keywords", { params: { ...queryParams, limit: 20, min_count: 1 } }),
        api.get("/research-intelligence/trends/citations", { params: queryParams }),
        api.get("/research-intelligence/emerging-topics", { params: { ...queryParams, recent_years: 2, min_count: 1 } }),
        api.get("/research-intelligence/hotspots", { params: { recent_years: 2, my_profile_only: myProfileOnly } }),
        api.get("/funding/recommendations", { params: { limit: 3, minimum_score: 50 } }),
        api.get("/research-intelligence/gaps", { params: selectedDomain ? { domain: selectedDomain } : {} }),
        api.get("/publications/recommendations", { params: { limit: 8, min_score: 10.0 } }),
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
      if (gapsRes.status === "fulfilled" && gapsRes.value.data.success) {
        setResearchGaps(gapsRes.value.data.data);
      } else if (gapsRes.status === "rejected") {
        setGapsError("Failed to discover research gaps. Please verify connection.");
      }
      if (paperRecRes.status === "fulfilled" && paperRecRes.value.data.success) {
        setPaperRecs(paperRecRes.value.data.data);
      } else if (paperRecRes.status === "rejected") {
        setRecsError("Failed to load paper recommendations. Please verify profile authentication.");
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
              Module 3 Engine
            </Badge>
          </div>
          <p className="text-xs text-slate-400 max-w-2xl">
            Data-driven scientific publication trajectories, domain market shares, statistical topic velocity,
            macro-corpus research gap discovery, and personalized profile-based paper recommendations.
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
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-8 gap-3">
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
            <p className="text-[10px] text-slate-400 mt-1">Indexed Papers</p>
          </div>
        </div>

        {/* Active Domains */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Domains</span>
            <Layers className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-300">
              {isLoading ? "..." : domainTrends?.total_domains ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Research Fields</p>
          </div>
        </div>

        {/* Unique Keywords */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Keywords</span>
            <Search className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-300">
              {isLoading ? "..." : keywordTrends?.total_keywords ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Tracked Topics</p>
          </div>
        </div>

        {/* Avg Citations */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Avg Citations</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-amber-300">
              {isLoading ? "..." : citationStats?.average_citations ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Impact per Paper</p>
          </div>
        </div>

        {/* Emerging Topics */}
        <div 
          onClick={() => setActiveTab("emerging")}
          className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all flex flex-col justify-between"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Emerging</span>
            <Zap className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-cyan-300">
              {isLoading ? "..." : emergingTopics?.total_emerging ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">High-Velocity</p>
          </div>
        </div>

        {/* Research Gaps (Module 3 Genuine Gap Closure) */}
        <div 
          onClick={() => setActiveTab("gaps")}
          className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-blue-500/40 cursor-pointer transition-all flex flex-col justify-between"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Research Gaps</span>
            <Compass className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-300">
              {isLoading ? "..." : researchGaps?.total_gaps ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Literature Horizons</p>
          </div>
        </div>

        {/* Recommended Papers (Module 3 Genuine Gap Closure) */}
        <div 
          onClick={() => setActiveTab("recommendations")}
          className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 cursor-pointer transition-all flex flex-col justify-between"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Paper Matches</span>
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-indigo-300">
              {isLoading ? "..." : paperRecs?.total_recommended ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Profile-Tailored</p>
          </div>
        </div>

        {/* Top Matched Funding */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider">Funding Matches</span>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div>
            <div className="text-2xl font-bold text-emerald-300">
              {isLoading ? "..." : fundingRecs?.total_recommended ?? 0}
            </div>
            <p className="text-[10px] text-slate-400 mt-1">Personalized RFPs</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs (Conforms strictly to Mentor Module 3 Structure) */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
            activeTab === "overview"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("trends")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
            activeTab === "trends"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Research Trends
        </button>
        <button
          onClick={() => setActiveTab("emerging")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
            activeTab === "emerging"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Emerging Topics
        </button>
        <button
          onClick={() => setActiveTab("hotspots")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
            activeTab === "hotspots"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Research Hotspots
        </button>
        <button
          onClick={() => setActiveTab("gaps")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "gaps"
              ? "bg-blue-600/20 text-blue-300 border border-blue-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Compass className="w-3.5 h-3.5 text-blue-400" />
          <span>Research Gap Discovery</span>
          {researchGaps?.total_gaps ? (
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-blue-500/20 text-[10px] text-blue-300 font-bold border border-blue-500/30">
              {researchGaps.total_gaps}
            </span>
          ) : null}
        </button>
        <button
          onClick={() => setActiveTab("recommendations")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap flex items-center gap-1.5 ${
            activeTab === "recommendations"
              ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Recommended Papers</span>
          {paperRecs?.total_recommended ? (
            <span className="ml-1 px-1.5 py-0.2 rounded-full bg-indigo-500/20 text-[10px] text-indigo-300 font-bold border border-indigo-500/30">
              {paperRecs.total_recommended}
            </span>
          ) : null}
        </button>
        <button
          onClick={() => setActiveTab("citations")}
          className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all whitespace-nowrap ${
            activeTab === "citations"
              ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Citation Impact
        </button>
      </div>

      {/* GLOBAL ERROR STATE */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <Button size="sm" variant="outline" onClick={fetchDashboardData} className="border-rose-500/30 text-rose-300 hover:bg-rose-500/20">
            Retry
          </Button>
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB: RESEARCH GAP DISCOVERY (DEDICATED FULL VIEW)               */}
      {/* ============================================================== */}
      {activeTab === "gaps" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Compass className="w-5 h-5 text-blue-400" />
                Macro-Corpus Research Gap Discovery
              </h2>
              <p className="text-xs text-slate-400 max-w-2xl">
                Deterministic gap discovery synthesized from publication abstracts, reported limitations,
                methodological bottlenecks, and future research directions across peer-reviewed literature.
              </p>
            </div>
            {selectedDomain && (
              <Badge variant="primary" className="bg-blue-500/10 text-blue-400 border-blue-500/30 text-xs py-1">
                Domain Filter: {selectedDomain}
              </Badge>
            )}
          </div>

          {/* Gaps Error State */}
          {gapsError && (
            <div data-testid="research-gaps-error" className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>{gapsError}</span>
              </div>
              <Button size="sm" variant="outline" onClick={fetchDashboardData} className="border-rose-500/30 text-rose-300">
                Retry
              </Button>
            </div>
          )}

          {/* Insufficient Data State */}
          {researchGaps?.status === "INSUFFICIENT_DATA" && (
            <div data-testid="research-gaps-insufficient" className="p-8 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-center space-y-3">
              <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
              <h3 className="text-base font-bold text-amber-200">
                Insufficient Literature Corpus for Deterministic Gap Discovery
              </h3>
              <p className="text-xs text-amber-300/80 max-w-xl mx-auto leading-relaxed">
                {researchGaps.message || "Macro-corpus gap discovery requires at least 2 peer-reviewed publications with abstracts and methodology statements in the selected domain. This safeguard ensures that identified research whitespace is backed by verifiable empirical literature rather than speculative synthesis."}
              </p>
              <div className="pt-2">
                <Link href="/publications">
                  <Button size="sm" className="bg-amber-600 hover:bg-amber-500 text-xs">
                    Browse All Publications
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {/* Empty State */}
          {researchGaps?.status === "NO_GAPS_IDENTIFIED" && (
            <div data-testid="research-gaps-empty" className="p-10 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-2">
              <Compass className="w-10 h-10 text-slate-500 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No Unaddressed Research Gaps Found</h4>
              <p className="text-xs text-slate-500">
                {researchGaps.message || "The analyzed corpus currently does not exhibit recurring limitation patterns in this scope."}
              </p>
            </div>
          )}

          {/* Populated Gaps List */}
          {researchGaps?.gaps && researchGaps.gaps.length > 0 && (
            <div data-testid="research-gaps-list" className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {researchGaps.gaps.map((gap, gIdx) => (
                <div
                  key={gIdx}
                  data-testid={`gap-card-${gIdx}`}
                  className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-blue-500/40 transition-all flex flex-col justify-between space-y-4 shadow-lg"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <Badge variant="primary" className="text-[10px] bg-blue-500/10 text-blue-400 border-blue-500/30">
                          {gap.domain}
                        </Badge>
                        <h3 className="text-sm font-bold text-white leading-snug">
                          {gap.gap}
                        </h3>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="inline-flex items-center px-2 py-0.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
                          {(gap.confidence * 100).toFixed(0)}% Confidence
                        </div>
                      </div>
                    </div>

                    {/* Literature Evidence Synthesis Quote */}
                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-1.5">
                      <div className="text-[11px] font-semibold text-slate-300 flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5 text-blue-400" />
                        <span>Empirical Literature Evidence</span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed italic">
                        "{gap.evidence}"
                      </p>
                    </div>

                    {/* Supporting Keywords */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">Supporting Topics:</span>
                      {gap.supporting_keywords.map((kw, kwIdx) => (
                        <span
                          key={kwIdx}
                          className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800/80 text-slate-300 border border-slate-700"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Supporting Publications Footer */}
                  <div className="flex items-center justify-between text-xs text-slate-400 pt-3 border-t border-slate-800/80">
                    <span className="text-[11px] text-slate-400">
                      Evidence Base: <strong className="text-white">{gap.evidence_count}</strong> {gap.evidence_count === 1 ? "paper" : "papers"}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] text-slate-500">Corpus References:</span>
                      {gap.supporting_publications.map((pId) => (
                        <Link key={pId} href={`/publications/${pId}`}>
                          <span className="text-[11px] px-2 py-0.5 rounded bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 font-mono transition-colors">
                            #{pId}
                          </span>
                        </Link>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB: RECOMMENDED PAPERS (DEDICATED FULL VIEW)                   */}
      {/* ============================================================== */}
      {activeTab === "recommendations" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <div className="space-y-1">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-400" />
                Profile-Based Paper Recommendations
              </h2>
              <p className="text-xs text-slate-400 max-w-2xl">
                Personalized, explainable relevance ranking computed deterministically from your research domains,
                keywords, and technical areas. Your own authored publications are excluded.
              </p>
            </div>
            <div className="text-[11px] text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
              Domains (40%) • Keywords (30%) • Tech Areas (15%) • History (10%) • Citations (5%)
            </div>
          </div>

          {/* Incomplete Profile Warning */}
          {paperRecs?.profile_completeness_warning && (
            <div data-testid="recommendations-profile-warning" className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <span>{paperRecs.profile_completeness_warning}</span>
              </div>
              <Link href="/profile">
                <Button size="sm" variant="outline" className="text-xs border-amber-500/30 text-amber-300 hover:bg-amber-500/20">
                  Update Profile
                </Button>
              </Link>
            </div>
          )}

          {/* Recs Error State */}
          {recsError && (
            <div data-testid="recommendations-error" className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>{recsError}</span>
              </div>
              <Button size="sm" variant="outline" onClick={fetchDashboardData} className="border-rose-500/30 text-rose-300">
                Retry
              </Button>
            </div>
          )}

          {/* Empty State */}
          {paperRecs?.recommendations && paperRecs.recommendations.length === 0 && (
            <div data-testid="recommendations-empty" className="p-10 rounded-2xl bg-slate-900/60 border border-slate-800 text-center space-y-3">
              <Sparkles className="w-10 h-10 text-slate-500 mx-auto" />
              <h4 className="text-sm font-semibold text-slate-300">No Recommended Papers Found</h4>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                No external publications matched your profile research topics or all matching papers are already authored by you. Update your profile keywords to discover new literature.
              </p>
              <div className="pt-2">
                <Link href="/profile">
                  <Button size="sm" variant="secondary" className="text-xs">
                    Update Research Profile
                  </Button>
                </Link>
              </div>
            </div>
          )}

          {/* Populated Recommendations List */}
          {paperRecs?.recommendations && paperRecs.recommendations.length > 0 && (
            <div data-testid="recommendations-list" className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {paperRecs.recommendations.map((rec) => (
                <div
                  key={rec.publication_id}
                  data-testid={`rec-card-${rec.publication_id}`}
                  className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 hover:border-indigo-500/40 transition-all flex flex-col justify-between space-y-4 shadow-lg"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          {rec.primary_domain && (
                            <Badge variant="secondary" className="text-[10px] border-slate-700">
                              {rec.primary_domain}
                            </Badge>
                          )}
                          {rec.year && (
                            <span className="text-[10px] text-slate-400 font-medium">
                              {rec.year}
                            </span>
                          )}
                        </div>
                        <Link href={`/publications/${rec.publication_id}`}>
                          <h3 className="text-sm font-bold text-white hover:text-indigo-400 transition-colors line-clamp-2">
                            {rec.title}
                          </h3>
                        </Link>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="inline-flex items-center px-2.5 py-1 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 font-bold text-xs">
                          {rec.relevance_score.toFixed(1)}% Match
                        </div>
                      </div>
                    </div>

                    {rec.authors && (
                      <p className="text-[11px] text-slate-400 line-clamp-1">
                        {rec.authors}
                      </p>
                    )}

                    {/* Explainability - Why Recommended */}
                    <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                      <span className="text-[10px] font-semibold uppercase text-indigo-400 tracking-wider block">
                        Why this paper was recommended:
                      </span>
                      <ul className="space-y-1">
                        {rec.reasons.map((reason, rIdx) => (
                          <li key={rIdx} className="flex items-start gap-1.5 text-xs text-slate-300">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                            <span className="leading-snug">{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Card Action Footer */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-xs">
                    {rec.doi ? (
                      <span className="font-mono text-[10px] text-slate-500 truncate max-w-[160px]">
                        {rec.doi}
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-600">ID #{rec.publication_id}</span>
                    )}
                    <Link href={`/publications/${rec.publication_id}`}>
                      <Button size="sm" variant="outline" className="text-xs border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/10">
                        View Publication & AI Analysis
                        <ChevronRight className="w-3.5 h-3.5 ml-1" />
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB: RESEARCH TRENDS & DOMAINS                                 */}
      {/* ============================================================== */}
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

      {/* ============================================================== */}
      {/* OVERVIEW PREVIEWS: RESEARCH GAPS & RECOMMENDED PAPERS          */}
      {/* ============================================================== */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Research Gaps Preview Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Compass className="w-4 h-4 text-blue-400" />
                  Research Gap Discovery
                </h3>
                <p className="text-[11px] text-slate-400">
                  Unaddressed research horizons extracted from cross-paper limitations and future directions
                </p>
              </div>
              <button
                onClick={() => setActiveTab("gaps")}
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1"
              >
                View All Gaps
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-3">
              {researchGaps?.status === "INSUFFICIENT_DATA" ? (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                  <div className="flex items-center gap-1.5 font-bold">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    <span>Insufficient literature corpus</span>
                  </div>
                  <p className="text-[11px] text-amber-300/80">
                    {researchGaps.message || "Minimum 2 publications required in this domain to extract grounded gaps."}
                  </p>
                </div>
              ) : researchGaps?.gaps && researchGaps.gaps.length > 0 ? (
                researchGaps.gaps.slice(0, 2).map((gap, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-blue-500/30 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <Badge variant="primary" className="text-[9px] bg-blue-500/10 text-blue-400 border-blue-500/30">
                        {gap.domain}
                      </Badge>
                      <span className="text-[10px] font-bold text-emerald-400">
                        {(gap.confidence * 100).toFixed(0)}% Confidence
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-white line-clamp-1">{gap.gap}</h4>
                    <p className="text-[11px] text-slate-400 line-clamp-2 italic">"{gap.evidence}"</p>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-slate-500 text-xs">
                  No active research gaps identified in this scope.
                </div>
              )}
            </div>
          </div>

          {/* Recommended Papers Preview Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Recommended Papers
                </h3>
                <p className="text-[11px] text-slate-400">
                  Explainable paper recommendations matching your researcher profile
                </p>
              </div>
              <button
                onClick={() => setActiveTab("recommendations")}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
              >
                View All Matches
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="space-y-3">
              {paperRecs?.recommendations && paperRecs.recommendations.length > 0 ? (
                paperRecs.recommendations.slice(0, 2).map((rec) => (
                  <div
                    key={rec.publication_id}
                    className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-indigo-500/30 transition-all space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-slate-400 font-medium">
                        {rec.primary_domain || "Research Paper"} • {rec.year || "Recent"}
                      </span>
                      <span className="text-[11px] font-bold text-indigo-300">
                        {rec.relevance_score.toFixed(1)}% Match
                      </span>
                    </div>
                    <Link href={`/publications/${rec.publication_id}`}>
                      <h4 className="text-xs font-bold text-white hover:text-indigo-400 transition-colors line-clamp-1">
                        {rec.title}
                      </h4>
                    </Link>
                    {rec.reasons && rec.reasons.length > 0 && (
                      <p className="text-[10px] text-slate-400 italic line-clamp-1">
                        • {rec.reasons[0]}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-slate-500 text-xs">
                  {paperRecs?.profile_completeness_warning ? (
                    <span className="text-amber-400">{paperRecs.profile_completeness_warning}</span>
                  ) : (
                    "No paper recommendations found matching your current profile."
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================== */}
      {/* TAB: EMERGING TOPICS & RESEARCH HOTSPOTS                       */}
      {/* ============================================================== */}
      {(activeTab === "overview" || activeTab === "emerging" || activeTab === "hotspots") && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Emerging Topics Card */}
          {(activeTab === "overview" || activeTab === "emerging") && (
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
          )}

          {/* Research Hotspots Card */}
          {(activeTab === "overview" || activeTab === "hotspots") && (
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
          )}
        </div>
      )}

      {/* ============================================================== */}
      {/* KEYWORD FREQUENCY TRAJECTORIES                                 */}
      {/* ============================================================== */}
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

      {/* ============================================================== */}
      {/* CITATION ANALYTICS & HIGH IMPACT PAPERS                        */}
      {/* ============================================================== */}
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

      {/* ============================================================== */}
      {/* SECTION: FUNDING OPPORTUNITY RECOMMENDATIONS RADAR              */}
      {/* ============================================================== */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-950/30 via-slate-900 to-indigo-950/30 border border-blue-900/40 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-emerald-400" />
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
