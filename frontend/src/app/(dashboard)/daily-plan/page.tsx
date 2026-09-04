"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  Clock,
  Coffee,
  Flame,
  Layers,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";
import { format } from "date-fns";
import { api } from "@/lib/api";
import { DailyPlan, TimeBlock } from "@/lib/types";

export default function DailyPlanPage() {
  const queryClient = useQueryClient();
  const todayStr = format(new Date(), "yyyy-MM-dd");

  const { data: plan, isLoading } = useQuery({
    queryKey: ["daily-plan", todayStr],
    queryFn: () => api.getDailyPlan(todayStr),
  });

  const generatePlanMutation = useMutation({
    mutationFn: () => api.generateDailyPlan(todayStr),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-plan", todayStr] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const updatePlanMutation = useMutation({
    mutationFn: (updates: Partial<DailyPlan>) =>
      api.updateDailyPlan(plan!.id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["daily-plan", todayStr] });
    },
  });

  const toggleBlock = (blockId: string) => {
    if (!plan) return;
    const updatedBlocks = plan.time_blocks_json.map((b) =>
      b.id === blockId ? { ...b, completed: !b.completed } : b
    );
    updatePlanMutation.mutate({ time_blocks_json: updatedBlocks });
  };

  const getBlockIcon = (type: TimeBlock["type"]) => {
    switch (type) {
      case "deep_work":
        return <Zap className="w-4 h-4 text-amber-400" />;
      case "habit":
        return <Flame className="w-4 h-4 text-rose-400" />;
      case "break":
        return <Coffee className="w-4 h-4 text-emerald-400" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-indigo-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Sparkles className="w-6 h-6 text-indigo-400" />
            AI Intelligent Daily Planner
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated time-blocking engine aligned with your working style and high-priority tasks
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => generatePlanMutation.mutate()}
            disabled={generatePlanMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${
                generatePlanMutation.isPending ? "animate-spin" : ""
              }`}
            />
            {generatePlanMutation.isPending ? "Optimizing..." : "Re-Plan My Day"}
          </button>
        </div>
      </div>

      {/* AI Strategy Summary Card */}
      {plan?.summary && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-slate-900 border border-indigo-500/30 shadow-md flex items-start gap-4">
          <div className="w-8 h-8 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
              Today&apos;s Strategic Flow ({plan.plan_date})
            </h3>
            <p className="text-xs text-slate-200 mt-1 leading-relaxed">{plan.summary}</p>
          </div>
        </div>
      )}

      {/* Time Blocks Sequence */}
      <div className="p-6 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Clock className="w-4 h-4 text-indigo-400" />
          Scheduled Focus Time-Blocks ({plan?.time_blocks_json?.length || 0})
        </h2>

        <div className="space-y-3 mt-4">
          {plan?.time_blocks_json && plan.time_blocks_json.length > 0 ? (
            plan.time_blocks_json.map((block) => (
              <div
                key={block.id}
                className={`p-4 rounded-xl border transition-all flex items-center justify-between gap-4 ${
                  block.completed
                    ? "bg-slate-900/40 border-slate-800/60 opacity-60"
                    : block.type === "deep_work"
                    ? "bg-indigo-950/20 border-indigo-500/30"
                    : block.type === "break"
                    ? "bg-emerald-950/20 border-emerald-500/20"
                    : "bg-slate-900/80 border-slate-800"
                }`}
              >
                <div className="flex items-center gap-3.5">
                  <button
                    onClick={() => toggleBlock(block.id)}
                    className={`w-6 h-6 rounded-lg border flex items-center justify-center transition-colors ${
                      block.completed
                        ? "bg-emerald-500 border-emerald-500 text-white"
                        : "border-slate-700 hover:border-indigo-500 text-transparent"
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                  </button>

                  <div className="flex items-center gap-2">
                    {getBlockIcon(block.type)}
                    <div>
                      <h3
                        className={`text-xs font-bold ${
                          block.completed ? "line-through text-slate-500" : "text-white"
                        }`}
                      >
                        {block.title}
                      </h3>
                      <span className="text-[10px] text-slate-400 font-mono uppercase">
                        {block.type.replace("_", " ")}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 font-mono text-xs font-semibold text-indigo-300 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  {block.start_time} - {block.end_time}
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-slate-500 text-xs">
              No daily schedule generated yet. Click &quot;Re-Plan My Day&quot; above to auto-generate!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
