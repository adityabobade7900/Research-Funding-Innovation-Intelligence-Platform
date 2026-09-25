import Link from "next/link";
import { Sparkles, ArrowRight, Shield, Award, Cpu, Search, Database, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  const roles = [
    {
      title: "Researcher",
      role: "researcher",
      badge: "Academic & R&D",
      description: "Discover high-match grant funding, analyze publication novelty, and identify prior-art whitespace.",
      icon: Search,
      color: "text-blue-400 border-blue-500/20 bg-blue-500/10",
    },
    {
      title: "Startup Founder",
      role: "startup_founder",
      badge: "Venture & Tech",
      description: "Map competitor patent landscapes, assess commercial viability, and find non-dilutive capital.",
      icon: Cpu,
      color: "text-purple-400 border-purple-500/20 bg-purple-500/10",
    },
    {
      title: "Innovation Manager",
      role: "innovation_manager",
      badge: "TTO & Enterprise",
      description: "Benchmark portfolio TRL readiness, track emerging research trends, and manage licensing pipelines.",
      icon: Award,
      color: "text-emerald-400 border-emerald-500/20 bg-emerald-500/10",
    },
    {
      title: "Administrator",
      role: "administrator",
      badge: "Governance",
      description: "Govern role-based permissions, monitor background ingestion health, and audit system activity.",
      icon: Shield,
      color: "text-amber-400 border-amber-500/20 bg-amber-500/10",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation Header */}
      <header className="border-b border-slate-800 bg-slate-950/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-glow">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white block">
                Research Intel
              </span>
              <span className="text-[10px] text-slate-400 -mt-1 block">
                Funding & Innovation Intelligence
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 rounded-lg transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-md hover:shadow-blue-500/20 transition-all flex items-center gap-1.5"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex flex-col justify-center">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/30 bg-blue-500/10 text-xs font-medium text-blue-400">
            <Sparkles className="w-3.5 h-3.5" />
            Stage 1 Repository Foundation Operational
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white">
            Transform Academic Research into{" "}
            <span className="text-gradient">Market Breakthroughs</span>
          </h1>

          <p className="text-lg text-slate-400 leading-relaxed">
            An intelligence platform combining vector search, patent landscape analysis,
            and an objective 5-pillar mathematical innovation scoring framework.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/register"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-3 rounded-xl shadow-lg hover:shadow-blue-500/25 transition-all flex items-center gap-2"
            >
              Create Account
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/login"
              className="glass-panel text-slate-200 hover:text-white font-medium px-6 py-3 rounded-xl border border-slate-700 hover:border-slate-600 transition-all"
            >
              Access Dashboard
            </Link>
          </div>
        </div>

        {/* 5-Pillar Innovation Formula Pill */}
        <div className="mt-16 glass-panel rounded-2xl p-6 max-w-4xl mx-auto w-full border border-slate-800">
          <div className="text-center mb-4">
            <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
              Objective 5-Pillar Innovation Scoring Formula
            </span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xl font-bold text-blue-400">30%</div>
              <div className="text-xs text-slate-400 mt-0.5">Research Novelty</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xl font-bold text-purple-400">20%</div>
              <div className="text-xs text-slate-400 mt-0.5">Patent Strength</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xl font-bold text-emerald-400">15%</div>
              <div className="text-xs text-slate-400 mt-0.5">Tech Maturity</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="text-xl font-bold text-amber-400">20%</div>
              <div className="text-xs text-slate-400 mt-0.5">Market Potential</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 col-span-2 sm:col-span-1">
              <div className="text-xl font-bold text-rose-400">15%</div>
              <div className="text-xs text-slate-400 mt-0.5">Funding Relevance</div>
            </div>
          </div>
        </div>

        {/* Roles Grid */}
        <div className="mt-16">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-white">Supported Stakeholder Roles</h2>
            <p className="text-sm text-slate-400 mt-1">
              Dedicated interfaces tailored for researchers, founders, innovation managers, and admins.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {roles.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.role}
                  className="glass-panel glass-panel-hover rounded-2xl p-6 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className={`p-2.5 rounded-xl border ${item.color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <Badge variant="secondary">{item.badge}</Badge>
                    </div>
                    <h3 className="font-semibold text-lg text-white">{item.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
                  </div>

                  <div className="pt-6">
                    <Link
                      href={`/register?role=${item.role}`}
                      className="text-xs font-medium text-blue-400 hover:text-blue-300 flex items-center gap-1 group"
                    >
                      Sign up as {item.title}
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        Research Funding & Innovation Intelligence Platform &copy; 2026. Built with FastAPI & Next.js.
      </footer>
    </div>
  );
}
