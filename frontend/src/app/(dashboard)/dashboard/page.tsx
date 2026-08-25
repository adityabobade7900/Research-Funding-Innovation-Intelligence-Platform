'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Search,
  Sliders,
  FileCode2,
  Briefcase,
  ArrowUpRight,
  TrendingUp,
  FileText,
  Clock,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { authStorage } from '@/lib/auth';
import { User } from '@/types/user';
import { api } from '@/lib/api';
import { formatRoleName } from '@/lib/utils';
import { CommandCenterOverviewResponse } from '@/types/command_center';

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [commandData, setCommandData] = useState<CommandCenterOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await api.get<{ data: CommandCenterOverviewResponse }>('/api/v1/command-center/overview');
      setCommandData(res.data.data);
    } catch (err: any) {
      console.error('Failed to load command center overview:', err);
      setErrorMsg('Unable to retrieve command center telemetry');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setUser(authStorage.getUser());
    fetchOverview();
  }, [fetchOverview]);

  const featureCards = [
    {
      title: 'Funding Radar & Matchmaking',
      desc: 'Semantic grant matching engine calculating vector eligibility against active research and patent portfolios.',
      href: '/funding',
      icon: Search,
      badge: 'M2 Funding',
      color: 'from-blue-500/20 to-blue-600/5 border-blue-500/30 text-blue-400',
    },
    {
      title: 'Technology & Whitespace Radar',
      desc: 'Cross-domain coverage density and statistical whitespace gap discovery for unpatented innovation niches.',
      href: '/technology-intelligence',
      icon: Sparkles,
      badge: 'M3B Whitespace',
      color: 'from-purple-500/20 to-purple-600/5 border-purple-500/30 text-purple-400',
    },
    {
      title: '5-Pillar Innovation Scoring',
      desc: 'Multi-factor composite scoring: Novelty (30%), Patent (20%), TRL (15%), Market (20%), Funding (15%).',
      href: '/scoring',
      icon: Sliders,
      badge: 'M3C Scoring',
      color: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 text-emerald-400',
    },
    {
      title: 'Executive Intelligence Dossier',
      desc: 'Unified decision-grade dossiers with SWOT assessments, 3-phase execution roadmaps, and Markdown exports.',
      href: '/reports',
      icon: FileText,
      badge: 'M4 Dossier',
      color: 'from-amber-500/20 to-amber-600/5 border-amber-500/30 text-amber-400',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Strategic Command Hero */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Strategic Intelligence Command Center
              </span>
              <span className="text-xs text-slate-400">
                {commandData?.is_profile_scoped ? 'Profile-Scoped Intelligence' : 'Global Platform Intelligence'}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              Welcome back, {user?.full_name || 'Innovator'}
            </h1>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
              {commandData?.role_metrics.role_headline ||
                'Unified innovation discovery, patent IP analysis, grant matchmaking, and translation pipeline.'}
            </p>
          </div>

          {commandData?.role_metrics && (
            <div className="flex flex-col sm:items-end gap-2">
              <Link
                href={commandData.role_metrics.focus_action_href}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition group"
              >
                <span>{commandData.role_metrics.recommended_focus_action}</span>
                <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </Link>
              <span className="text-[11px] text-slate-400">
                Role: <strong className="text-indigo-300 capitalize">{user ? formatRoleName(user.role) : 'Researcher'}</strong>
              </span>
            </div>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 font-bold">×</button>
        </div>
      )}

      {/* Unified Metric Scoreboard (6 Tiles) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* 1. Innovation Score */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Innovation Score</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-extrabold text-white">{commandData?.average_innovation_score ?? 0}</span>
            <span className="text-[10px] text-slate-500">/ 100</span>
          </div>
          <span className="text-[9px] text-indigo-300 block mt-1">Composite 5-Pillar</span>
        </div>

        {/* 2. Commercialization Readiness */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Commercial Readiness</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-extrabold text-emerald-400">{commandData?.average_readiness_score ?? 0}</span>
            <span className="text-[10px] text-slate-500">/ 100</span>
          </div>
          <span className="text-[9px] text-emerald-300 block mt-1">Market Viability</span>
        </div>

        {/* 3. TRL Maturity */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Maturity Level</span>
          <div className="text-sm font-extrabold text-indigo-400 mt-1 truncate">
            {commandData?.dominant_trl_stage || 'TRL 1-9'}
          </div>
          <span className="text-[9px] text-slate-400 block mt-1">TRL Rule Engine</span>
        </div>

        {/* 4. Primary Pathway */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Top Translation Route</span>
          <div className="text-xs font-bold text-white mt-1 truncate">
            {commandData?.top_recommended_pathway?.replace(/_/g, ' ') || 'STARTUP SPINOUT'}
          </div>
          <span className="text-[9px] text-cyan-300 block mt-1">Prioritized Action</span>
        </div>

        {/* 5. Identified Grant Capital */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Tracked Grant Capital</span>
          <div className="text-xl font-extrabold text-cyan-400 mt-1">
            ${(((commandData?.total_grant_pool_usd ?? 0) / 1000000)).toFixed(1)}M
          </div>
          <span className="text-[9px] text-slate-400 block mt-1">
            {commandData?.total_funding_opportunities ?? 0} Solicitations
          </span>
        </div>

        {/* 6. Papers / Patents */}
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-sm">
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Portfolio Scale</span>
          <div className="text-xl font-extrabold text-white mt-1">
            {commandData?.total_publications ?? 0}p • {commandData?.total_patents ?? 0}pat
          </div>
          <span className="text-[9px] text-slate-400 block mt-1">Indexed Claims & DOIs</span>
        </div>
      </div>

      {/* Core Workflow Cards (4 Modules) */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold text-white">Platform Intelligence Workflows</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {featureCards.map((feat) => {
            const Icon = feat.icon;
            return (
              <Link
                key={feat.title}
                href={feat.href}
                className="group relative p-5 rounded-2xl bg-slate-900/80 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-3 shadow-sm hover:shadow-md"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-br ${feat.color} border`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 font-semibold">{feat.badge}</span>
                  </div>
                  <h3 className="text-xs font-bold text-white mt-3 group-hover:text-indigo-300 transition">
                    {feat.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed line-clamp-2">
                    {feat.desc}
                  </p>
                </div>
                <div className="flex items-center gap-1 text-[10px] font-bold text-indigo-400 group-hover:text-indigo-300 transition pt-2 border-t border-slate-800/80">
                  <span>Launch Module</span>
                  <ArrowUpRight className="w-3 h-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Two-Column Command Grid: Activity Feed & Upcoming Grant Deadlines */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2/3): Live Multi-Stream Activity Feed */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-indigo-400" />
              Live Multi-Stream Intelligence Feed
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Real-Time</span>
          </div>

          <div className="space-y-3">
            {commandData?.recent_activity.map((act) => (
              <div
                key={act.id}
                className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-start justify-between gap-4 hover:bg-slate-950 transition"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                      act.activity_type === 'PUBLICATION'
                        ? 'bg-blue-500/10 text-blue-400'
                        : act.activity_type === 'PATENT'
                        ? 'bg-purple-500/10 text-purple-400'
                        : 'bg-emerald-500/10 text-emerald-400'
                    }`}>
                      {act.badge_label}
                    </span>
                    <span className="text-xs font-bold text-slate-200">{act.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{act.description}</p>
                </div>
                <Link
                  href={act.action_href}
                  className="shrink-0 p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
                >
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column (1/3): Upcoming Grant Deadlines & Whitespace Gaps */}
        <div className="space-y-6">
          {/* Grant Deadlines */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                Upcoming Grant Deadlines
              </h3>
              <Link href="/funding" className="text-[10px] text-cyan-400 hover:underline">
                View All
              </Link>
            </div>

            <div className="space-y-2.5">
              {commandData?.upcoming_grant_deadlines.map((grant) => (
                <div key={grant.id} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1">
                  <div className="text-xs font-bold text-slate-200 line-clamp-1">{grant.title}</div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400">
                    <span className="text-cyan-300">{grant.agency}</span>
                    <span className="font-mono text-emerald-400">
                      {grant.amount ? `$${(grant.amount / 1e6).toFixed(1)}M` : 'Open'}
                    </span>
                  </div>
                  {grant.deadline && (
                    <div className="text-[9px] text-slate-500 font-mono">
                      Deadline: {new Date(grant.deadline).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Whitespace Candidates */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                Discovered Whitespace Gaps
              </h3>
              <Link href="/technology-intelligence" className="text-[10px] text-purple-400 hover:underline">
                Explore
              </Link>
            </div>

            <div className="space-y-1.5">
              {commandData?.top_whitespace_areas.map((ws, idx) => (
                <div key={idx} className="px-3 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-purple-300 font-medium flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                  <span>{ws}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* System Operational Badge */}
      <div className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Platform Intelligence Hub: <strong>100% Operational</strong></span>
        </div>
        <span className="font-mono text-[10px] text-slate-500">M1–M6 Full Integration Active</span>
      </div>
    </div>
  );
}
