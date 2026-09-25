"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Sparkles,
  LayoutDashboard,
  Search,
  TrendingUp,
  FileCode2,
  Sliders,
  Briefcase,
  FileText,
  Shield,
  Bell,
  LogOut,
  User as UserIcon,
  BookOpen,
} from "lucide-react";
import { authStorage } from "@/lib/auth";
import { User } from "@/types/user";
import { Badge } from "@/components/ui/badge";
import { formatRoleName } from "@/lib/utils";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const currentUser = authStorage.getUser();
    if (!currentUser || !authStorage.isAuthenticated()) {
      router.push("/login");
    } else {
      setUser(currentUser);
    }
    setIsLoading(false);
  }, [router]);

  const handleLogout = () => {
    authStorage.clearAuth();
    router.push("/login");
  };

  const navItems = [
    { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
    { label: "Research Profile", href: "/profile", icon: UserIcon },
    { label: "Publications", href: "/publications", icon: BookOpen },
    { label: "Funding Radar", href: "/funding", icon: Search, badge: "AI Match" },
    { label: "Research Intelligence", href: "/research-intelligence", icon: TrendingUp, badge: "Analytics" },
    { label: "Patent Landscape", href: "/patents", icon: FileCode2 },
    { label: "Tech Intelligence", href: "/technology-intelligence", icon: Sparkles, badge: "Whitespace" },
    { label: "Innovation Scoring", href: "/scoring", icon: Sliders, badge: "5-Pillar" },
    { label: "Commercialization", href: "/commercialization", icon: Briefcase },
    { label: "Executive Reports", href: "/reports", icon: FileText },
  ];

  if (user?.role === "administrator" || user?.is_superuser) {
    navItems.push({ label: "Administration", href: "/admin", icon: Shield, badge: "Admin" });
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="flex items-center gap-2 text-slate-400 text-sm">
          <Sparkles className="w-4 h-4 text-blue-400 animate-spin" />
          Loading workspace...
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/40 backdrop-blur-xl flex flex-col justify-between hidden md:flex">
        <div>
          {/* Logo */}
          <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800/80">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-glow">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <span className="font-bold text-sm tracking-tight text-white block">
                Research Intel
              </span>
              <span className="text-[10px] text-slate-400 -mt-1 block">
                Intelligence Platform
              </span>
            </div>
          </div>

          {/* Nav links */}
          <nav className="p-4 space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && !isActive && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Card & Logout */}
        <div className="p-4 border-t border-slate-800/80">
          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0">
                <UserIcon className="w-4 h-4 text-slate-300" />
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-medium text-white truncate">{user?.full_name}</p>
                <p className="text-[10px] text-slate-400 truncate capitalize">{user ? formatRoleName(user.role) : ""}</p>
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-medium text-rose-400 hover:bg-rose-500/10 transition-colors border border-transparent hover:border-rose-500/20"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/40 backdrop-blur-md px-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">Workspace:</span>
            <Badge variant="primary" className="capitalize">
              {user ? formatRoleName(user.role) : "Loading..."}
            </Badge>
          </div>

          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors relative">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
            </button>
            <div className="text-right hidden sm:block">
              <p className="text-xs font-semibold text-white">{user?.full_name}</p>
              <p className="text-[10px] text-slate-400">{user?.email}</p>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
