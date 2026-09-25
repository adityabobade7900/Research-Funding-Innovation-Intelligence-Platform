"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, Lock, Mail, AlertCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { authStorage } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await api.post("/auth/login", {
        email,
        password,
      });

      if (response.data?.success) {
        const { access_token, refresh_token, user } = response.data.data;
        authStorage.setTokens(access_token, refresh_token);
        authStorage.setUser(user);
        router.push("/dashboard");
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Invalid email or password";
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full space-y-8 glass-panel p-8 rounded-2xl border border-slate-800 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 shadow-glow mb-2">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Sign in to Research Intel
          </h2>
          <p className="text-xs text-slate-400">
            Enter your credentials to access funding and innovation dashboards
          </p>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            placeholder="researcher@university.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />

          <Button
            type="submit"
            className="w-full py-2.5 mt-2"
            isLoading={isLoading}
          >
            Sign In
          </Button>
        </form>

        <div className="text-center text-xs text-slate-400 pt-4 border-t border-slate-800/80">
          Don't have an account?{" "}
          <Link href="/register" className="text-blue-400 hover:text-blue-300 font-medium">
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
}
