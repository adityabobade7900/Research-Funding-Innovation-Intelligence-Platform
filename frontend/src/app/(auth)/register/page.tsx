"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import { UserRole } from "@/types/user";

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialRole = (searchParams.get("role") as UserRole) || "researcher";

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>(initialRole);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const roleParam = searchParams.get("role") as UserRole;
    if (roleParam) {
      setRole(roleParam);
    }
  }, [searchParams]);

  const roles = [
    { value: "researcher", label: "Researcher", desc: "Academic & Scientific R&D" },
    { value: "startup_founder", label: "Startup Founder", desc: "Commercial & Deep-Tech" },
    { value: "innovation_manager", label: "Innovation Manager", desc: "TTO & IP Portfolio" },
    { value: "administrator", label: "Administrator", desc: "System & Governance" },
  ];

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await api.post("/auth/register", {
        full_name: fullName,
        email,
        password,
        role,
      });

      if (response.data?.success) {
        // Auto login on successful registration
        const loginResp = await api.post("/auth/login", {
          email,
          password,
        });

        if (loginResp.data?.success) {
          const { access_token, refresh_token, user } = loginResp.data.data;
          authStorage.setTokens(access_token, refresh_token);
          authStorage.setUser(user);
          router.push("/dashboard");
        } else {
          router.push("/login");
        }
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Registration failed. Please check your inputs.";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-lg w-full space-y-8 glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-glow mb-2">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Create an Account
        </h2>
        <p className="text-xs text-slate-400">
          Select your platform role to configure your personalized intelligence workspace
        </p>
      </div>

      {errorMessage && (
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-4">
        <Input
          label="Full Name"
          placeholder="Dr. Jane Doe"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />

        <Input
          label="Email Address"
          type="email"
          placeholder="jane.doe@university.edu"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />

        <Input
          label="Password"
          type="password"
          placeholder="Minimum 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          autoComplete="new-password"
        />

        {/* Role Selector */}
        <div className="space-y-1.5 pt-1">
          <label className="block text-xs font-medium text-slate-300">
            Select Primary Role
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {roles.map((r) => {
              const isSelected = role === r.value;
              return (
                <button
                  type="button"
                  key={r.value}
                  onClick={() => setRole(r.value as UserRole)}
                  className={`p-3 rounded-xl border text-left transition-all relative ${
                    isSelected
                      ? "bg-blue-600/10 border-blue-500/50 shadow-sm"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-semibold ${isSelected ? "text-blue-400" : "text-slate-200"}`}>
                      {r.label}
                    </span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-400" />}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{r.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        <Button
          type="submit"
          className="w-full py-2.5 mt-4"
          isLoading={isLoading}
        >
          Complete Registration
        </Button>
      </form>

      <div className="text-center text-xs text-slate-400 pt-4 border-t border-slate-800/80">
        Already have an account?{" "}
        <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium">
          Sign in
        </Link>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <Suspense fallback={<div className="text-slate-400 text-sm">Loading registration...</div>}>
        <RegisterForm />
      </Suspense>
    </div>
  );
}
