"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  Award,
  CheckCircle2,
  Compass,
  Lightbulb,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";

export default function WeeklyReviewPage() {
  const queryClient = useQueryClient();

  const { data: reviews = [], isLoading } = useQuery({
    queryKey: ["weekly-reviews"],
    queryFn: () => api.getWeeklyReviews(),
  });

  const generateReviewMutation = useMutation({
    mutationFn: () => api.generateWeeklyReview(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["weekly-reviews"] });
    },
  });

  const latestReview = reviews.length > 0 ? reviews[0] : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Compass className="w-6 h-6 text-purple-400" />
            Weekly AI Retrospective & Review
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated retrospective analyzing output, habit streaks, friction points, and recommendations
          </p>
        </div>

        <button
          onClick={() => generateReviewMutation.mutate()}
          disabled={generateReviewMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-purple-600/20 transition-all"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${
              generateReviewMutation.isPending ? "animate-spin" : ""
            }`}
          />
          {generateReviewMutation.isPending ? "Synthesizing..." : "Generate Retrospective"}
        </button>
      </div>

      {latestReview ? (
        <div className="space-y-6">
          {/* Executive Summary Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-950/40 via-indigo-950/30 to-slate-900 border border-purple-500/30 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase font-mono tracking-wider text-purple-300 font-semibold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                Retrospective Period: {latestReview.start_date} &rarr; {latestReview.end_date}
              </span>
              <span className="text-xs px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-mono font-bold border border-purple-500/30">
                Score: {latestReview.productivity_score}/100
              </span>
            </div>

            <p className="text-sm text-slate-200 leading-relaxed font-sans font-medium">
              {latestReview.summary}
            </p>
          </div>

          {/* Three Column Breakdown: Wins, Bottlenecks, Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Wins */}
            <div className="p-5 rounded-2xl bg-[#111726]/80 border border-emerald-500/30 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" />
                <h2 className="text-xs font-bold text-emerald-300 uppercase tracking-wider">
                  Weekly Wins
                </h2>
              </div>
              <ul className="space-y-2.5">
                {latestReview.wins_json.map((win, idx) => (
                  <li
                    key={idx}
                    className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-xs text-slate-200 leading-relaxed flex items-start gap-2.5"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{win}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Bottlenecks */}
            <div className="p-5 rounded-2xl bg-[#111726]/80 border border-rose-500/30 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <h2 className="text-xs font-bold text-rose-300 uppercase tracking-wider">
                  Friction & Bottlenecks
                </h2>
              </div>
              <ul className="space-y-2.5">
                {latestReview.bottlenecks_json.map((b, idx) => (
                  <li
                    key={idx}
                    className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/20 text-xs text-slate-200 leading-relaxed flex items-start gap-2.5"
                  >
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span>{b}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div className="p-5 rounded-2xl bg-[#111726]/80 border border-indigo-500/30 shadow-sm space-y-3">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-indigo-400" />
                <h2 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
                  Strategic Next Actions
                </h2>
              </div>
              <ul className="space-y-2.5">
                {latestReview.recommendations_json.map((rec, idx) => (
                  <li
                    key={idx}
                    className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 text-xs text-slate-200 leading-relaxed flex items-start gap-2.5"
                  >
                    <Zap className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 rounded-2xl bg-[#111726]/60 border border-slate-800 text-center space-y-3">
          <p className="text-xs text-slate-400">
            No weekly reviews found. Click &quot;Generate Retrospective&quot; above to synthesize your first AI review!
          </p>
        </div>
      )}
    </div>
  );
}
