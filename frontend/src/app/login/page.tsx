"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { Lock, Mail, Sparkles, ArrowRight, User } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && localStorage.getItem("personalix_token")) {
      router.push("/dashboard");
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await api.login(email.trim(), password);
      } else {
        const name = fullName.trim() || email.split("@")[0] || "User";
        await api.register(email.trim(), password, name);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setDemoLoading(true);
    setError("");
    try {
      await api.demoLogin();
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Demo login failed");
    } finally {
      setDemoLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] flex items-center justify-center p-4">
      {/* Background gradient orbs */}
      <div className="fixed top-0 right-0 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md space-y-6">
        {/* Logo */}
        <div className="text-center">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-2xl shadow-indigo-500/30 mb-4">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-black text-white tracking-tight">
            Personalix <span className="text-indigo-400">OS</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            AI-Powered Personal Operating System
          </p>
        </div>

        {/* Card */}
        <div className="bg-[#111726] border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
          {/* Toggle Tabs */}
          <div className="flex bg-slate-900 rounded-xl p-1 border border-slate-800">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                mode === "login"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setMode("register")}
              className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                mode === "register"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Create Account
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">Full Name</label>
                <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 focus-within:border-indigo-500 transition-colors">
                  <User className="w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Alex Mercer"
                    required
                    className="bg-transparent border-none outline-none text-white text-xs w-full placeholder-slate-500"
                  />
                </div>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Email</label>
              <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 focus-within:border-indigo-500 transition-colors">
                <Mail className="w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="bg-transparent border-none outline-none text-white text-xs w-full placeholder-slate-500"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Password</label>
              <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 focus-within:border-indigo-500 transition-colors">
                <Lock className="w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="bg-transparent border-none outline-none text-white text-xs w-full placeholder-slate-500"
                />
              </div>
            </div>

            {error && (
              <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition-all"
            >
              {loading ? "Authenticating..." : mode === "login" ? "Sign In" : "Create Account"}
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-800" />
            </div>
            <div className="relative flex justify-center">
              <span className="px-3 text-[11px] text-slate-500 bg-[#111726]">or</span>
            </div>
          </div>

          <button
            onClick={handleDemoLogin}
            disabled={demoLoading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            {demoLoading ? "Loading Demo..." : "Try Demo Account (Alex Mercer)"}
          </button>
        </div>

        <p className="text-center text-[11px] text-slate-500">
          Personalix OS — Production-grade AI Personal Operating System
        </p>
      </div>
    </div>
  );
}
