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
  const rawRole = searchParams.get("role") as UserRole;
  const initialRole: UserRole = (rawRole && rawRole !== "administrator") ? rawRole : "researcher";

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [institution, setInstitution] = useState("");
  const [designation, setDesignation] = useState("");
  const [country, setCountry] = useState("");
  const [role, setRole] = useState<UserRole>(initialRole);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const roleParam = searchParams.get("role") as UserRole;
    if (roleParam && roleParam !== "administrator") {
      setRole(roleParam);
    }
  }, [searchParams]);

  const roles = [
    { value: "researcher", label: "Researcher", desc: "Academic & Scientific R&D" },
    { value: "startup_founder", label: "Startup Founder", desc: "Commercial & Deep-Tech" },
    { value: "innovation_manager", label: "Innovation Manager", desc: "TTO & IP Portfolio" },
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
        phone: phone || undefined,
        institution: institution || undefined,
        designation: designation || undefined,
        country: country || undefined,
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
    <div className="max-w-3xl w-full space-y-6 sm:space-y-8 glass-panel p-6 sm:p-10 rounded-2xl border border-slate-800 shadow-2xl">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-glow mb-1">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          Create an Account
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto">
          Select your platform role to configure your personalized intelligence workspace
        </p>
      </div>

      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs sm:text-sm flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-5">
        {/* Row 1: Full Name (Full Width) */}
        <div>
          <Input
            label="Full Name *"
            placeholder="Dr. Jane Doe"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>

        {/* Row 2: Email Address & Phone Number (2 columns on sm+) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Email Address *"
            type="email"
            placeholder="jane.doe@university.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />

          <Input
            label="Phone Number"
            type="tel"
            placeholder="+1 (555) 000-0000"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>

        {/* Row 3: Password & Organization / Institution (2 columns on sm+) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Password *"
            type="password"
            placeholder="Minimum 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />

          <Input
            label="Organization / Institution"
            placeholder="MIT / DeepTech Inc."
            value={institution}
            onChange={(e) => setInstitution(e.target.value)}
          />
        </div>

        {/* Row 4: Designation / Role Title & Country (2 columns on sm+) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Input
            label="Designation / Role Title"
            placeholder="Associate Professor / CTO"
            value={designation}
            onChange={(e) => setDesignation(e.target.value)}
          />

          <Input
            label="Country"
            placeholder="United States"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
        </div>

        {/* Role Selector: 3 columns horizontally on md+, stacked on mobile */}
        <div className="space-y-2 pt-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
            Select Primary Role
          </label>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {roles.map((r) => {
              const isSelected = role === r.value;
              return (
                <button
                  type="button"
                  key={r.value}
                  onClick={() => setRole(r.value as UserRole)}
                  className={`p-3.5 rounded-xl border text-left transition-all relative flex flex-col justify-between ${
                    isSelected
                      ? "bg-blue-600/10 border-blue-500/50 shadow-sm ring-1 ring-blue-500/20"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/90"
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span className={`text-xs font-semibold ${isSelected ? "text-blue-400" : "text-slate-200"}`}>
                      {r.label}
                    </span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0" />}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">{r.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full py-3 mt-4 text-sm font-semibold shadow-lg shadow-blue-600/20"
          isLoading={isLoading}
        >
          Complete Registration
        </Button>
      </form>

      <div className="text-center text-xs sm:text-sm text-slate-400 pt-4 border-t border-slate-800/80">
        Already have an account?{" "}
        <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
          Sign in
        </Link>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-8 sm:py-12">
      <Suspense fallback={<div className="text-slate-400 text-sm">Loading registration...</div>}>
        <RegisterForm />
      </Suspense>
    </div>
  );
}
