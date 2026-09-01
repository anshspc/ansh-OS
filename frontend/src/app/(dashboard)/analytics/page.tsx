"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  ArrowUpRight,
  Award,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  Flame,
  HelpCircle,
  Lightbulb,
  ShieldCheck,
  Target,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const { data: scoreData, isLoading } = useQuery({
    queryKey: ["productivity-score"],
    queryFn: () => api.getProductivityScore(),
  });

  const { data: activities = [] } = useQuery({
    queryKey: ["activities"],
    queryFn: () => api.getRecentActivities(),
  });

  const breakdown = scoreData?.breakdown || {
    task_completion: 0,
    goal_progress: 0,
    focus_consistency: 0,
    habit_consistency: 0,
    deadline_management: 0,
  };

  const metricComponents = [
    {
      title: "Task Completion Throughput",
      weight: "25% Weight",
      score: breakdown.task_completion,
      max: 25,
      icon: CheckCircle2,
      color: "#6366f1",
      desc: "Proportion of active tasks successfully resolved vs backlog",
    },
    {
      title: "Goal & Milestone Alignment",
      weight: "20% Weight",
      score: breakdown.goal_progress,
      max: 20,
      icon: Target,
      color: "#10b981",
      desc: "Cumulative velocity towards long-term quarterly objectives",
    },
    {
      title: "Focus Block Consistency",
      weight: "20% Weight",
      score: breakdown.focus_consistency,
      max: 20,
      icon: Clock,
      color: "#06b6d4",
      desc: "Scheduled deep work sessions protected without context switching",
    },
    {
      title: "Habit Streak Adherence",
      weight: "20% Weight",
      score: breakdown.habit_consistency,
      max: 20,
      icon: Flame,
      color: "#f59e0b",
      desc: "Daily recurring rituals logged over rolling 7-day window",
    },
    {
      title: "Deadline Reliability",
      weight: "15% Weight",
      score: breakdown.deadline_management,
      max: 15,
      icon: ShieldCheck,
      color: "#ec4899",
      desc: "On-time delivery rate with zero overdue task penalties",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
          <BarChart3 className="w-6 h-6 text-indigo-400" />
          Explainable Productivity Analytics
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Mathematical composite score derived directly from 5 live data dimensions with zero black-box metrics
        </p>
      </div>

      {/* Main Score Hero Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-500/30 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2 text-center md:text-left">
          <div className="flex items-center gap-2 justify-center md:justify-start">
            <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider">
              Composite Performance Score
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono font-bold">
              Tier {scoreData?.grade || "A"}
            </span>
          </div>

          <div className="flex items-baseline gap-3 justify-center md:justify-start">
            <span className="text-5xl font-black text-white font-mono tracking-tight">
              {scoreData?.total_score || 0}
            </span>
            <span className="text-sm text-slate-400 font-medium">/ 100 max</span>
          </div>

          <p className="text-xs text-slate-300 max-w-xl leading-relaxed">
            {scoreData?.explanation}
          </p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-2 w-full md:w-72">
          <span className="font-bold text-slate-300 flex items-center gap-1.5">
            <Lightbulb className="w-4 h-4 text-amber-400" /> Key Insights
          </span>
          <ul className="space-y-1.5 text-slate-400">
            {scoreData?.insights.map((insight, idx) => (
              <li key={idx} className="text-[11px] leading-relaxed">
                • {insight}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 5 Mathematical Dimensions Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metricComponents.map((metric, idx) => {
          const Icon = metric.icon;
          const percentage = ((metric.score / metric.max) * 100).toFixed(0);
          return (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-[#111726]/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-white"
                    style={{ backgroundColor: `${metric.color}25`, color: metric.color }}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-bold text-white">{metric.title}</span>
                </div>
                <span className="text-[10px] font-mono text-slate-500">{metric.weight}</span>
              </div>

              <p className="text-[11px] text-slate-400 leading-relaxed">{metric.desc}</p>

              <div className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono">
                  <span className="text-slate-400">Earned Points</span>
                  <span className="text-white font-bold">
                    {metric.score} / {metric.max} pts ({percentage}%)
                  </span>
                </div>
                <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: metric.color,
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Real-time Activity Audit Feed */}
      <div className="p-6 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-white flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          Real-Time Audit Activity Log
        </h2>

        <div className="divide-y divide-slate-800/80 border-t border-slate-800/80 mt-3">
          {activities.map((act) => (
            <div key={act.id} className="py-3 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-indigo-500 shrink-0" />
                <div>
                  <span className="font-semibold text-slate-200 uppercase tracking-wider text-[10px] font-mono mr-2 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                    {act.action.replace("_", " ")}
                  </span>
                  <span className="text-slate-400">
                    {act.details?.title || act.details?.name || act.entity_type}
                  </span>
                </div>
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                {new Date(act.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
