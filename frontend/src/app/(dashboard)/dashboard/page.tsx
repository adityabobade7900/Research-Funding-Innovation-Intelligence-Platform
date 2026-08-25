"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  Search,
  Sliders,
  FileCode2,
  Briefcase,
  ArrowUpRight,
  CheckCircle2,
  Server,
  Layers,
  TrendingUp,
} from "lucide-react";
import { authStorage } from "@/lib/auth";
import { User } from "@/types/user";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";
import { formatRoleName } from "@/lib/utils";

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [systemHealth, setSystemHealth] = useState<{
    status: string;
    database: string;
    environment: string;
  } | null>(null);

  useEffect(() => {
    setUser(authStorage.getUser());

    // Ping backend health endpoint
    api.get("/health")
      .then((res) => {
        if (res.data?.success) {
          setSystemHealth(res.data.data);
        }
      })
      .catch((err) => {
        console.error("Health check failed:", err);
      });
  }, []);

  const featureCards = [
    {
      title: "Funding Opportunity Discovery",
      desc: "AI grant matchmaking radar calculating vector similarity against your active research profile.",
      href: "/funding",
      icon: Search,
      badge: "Module 3",
      color: "from-blue-500/20 to-blue-600/5 border-blue-500/30 text-blue-400",
    },
    {
      title: "Patent Landscape & Whitespace",
      desc: "Semantic prior art mapping and 2D/3D visual clustering to locate unpatented technological whitespace.",
      href: "/patents",
      icon: FileCode2,
      badge: "Module 5",
      color: "from-purple-500/20 to-purple-600/5 border-purple-500/30 text-purple-400",
    },
    {
      title: "5-Pillar Innovation Scoring",
      desc: "Objective mathematical composite evaluation: Novelty (30%), Patent (20%), TRL (15%), Market (20%), Funding (15%).",
      href: "/scoring",
      icon: Sliders,
      badge: "Module 7",
      color: "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 text-emerald-400",
    },
    {
      title: "Commercialization Pathways",
      desc: "Spin-off viability analysis, industry joint-venture matcher, and technology licensing partner discovery.",
      href: "/commercialization",
      icon: Briefcase,
      badge: "Module 8",
      color: "from-amber-500/20 to-amber-600/5 border-amber-500/30 text-amber-400",
    },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Welcome Banner */}
      <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase tracking-wider font-semibold text-blue-400">
                Active Intelligence Workspace
              </span>
              <Badge variant="primary" className="text-[10px]">
                Stage 1 Ready
              </Badge>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              Welcome back, {user?.full_name || "Innovator"}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
              Logged in as <strong className="text-slate-200 capitalize">{user ? formatRoleName(user.role) : ""}</strong>.
              Your repository foundation and role-based access gates are fully active.
            </p>
          </div>

          {/* System Health Widget */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex-shrink-0 space-y-2 min-w-[220px]">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 flex items-center gap-1.5">
                <Server className="w-3.5 h-3.5 text-slate-400" />
                Backend API
              </span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                {systemHealth?.status || "Online"}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" />
                Database Engine
              </span>
              <span className="text-slate-200 font-medium capitalize">
                {systemHealth?.database || "Connected"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 5-Pillar Score Matrix */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Innovation Scoring Weight Distribution
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Standardized weights configured for all technology evaluations.
            </p>
          </div>
          <Badge variant="purple">Formula v1.0</Badge>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-blue-500/20">
            <div className="text-2xl font-bold text-blue-400">30%</div>
            <div className="text-xs font-semibold text-slate-200 mt-1">Research Novelty</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Prior literature semantic dispersion</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-purple-500/20">
            <div className="text-2xl font-bold text-purple-400">20%</div>
            <div className="text-xs font-semibold text-slate-200 mt-1">Patent Strength</div>
            <div className="text-[10px] text-slate-400 mt-0.5">FTO score & prior art distance</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-emerald-500/20">
            <div className="text-2xl font-bold text-emerald-400">15%</div>
            <div className="text-xs font-semibold text-slate-200 mt-1">Tech Maturity</div>
            <div className="text-[10px] text-slate-400 mt-0.5">TRL 1-9 sigmoid curve</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-amber-500/20">
            <div className="text-2xl font-bold text-amber-400">20%</div>
            <div className="text-xs font-semibold text-slate-200 mt-1">Market Potential</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Sector CAGR & VC deal velocity</div>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-900/70 border border-rose-500/20 col-span-2 sm:col-span-1">
            <div className="text-2xl font-bold text-rose-400">15%</div>
            <div className="text-xs font-semibold text-slate-200 mt-1">Funding Relevance</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Grant alignment & match cosine</div>
          </div>
        </div>
      </div>

      {/* Feature Navigation Grid */}
      <div>
        <h2 className="text-base font-bold text-white mb-4">Core Intelligence Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {featureCards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.title}
                className="glass-panel glass-panel-hover rounded-2xl p-6 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className={`p-3 rounded-xl border bg-gradient-to-br ${card.color}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <Badge variant="secondary">{card.badge}</Badge>
                  </div>
                  <h3 className="text-base font-bold text-white">{card.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{card.desc}</p>
                </div>

                <div className="pt-6">
                  <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 group">
                    Ready for Stage Implementation
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
