"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Calendar,
  CheckCircle2,
  Clock,
  Flame,
  FolderKanban,
  Plus,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const queryClient = useQueryClient();

  const { data: summary, isLoading, error } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => api.getDashboardSummary(),
  });

  const toggleTaskMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.updateTask(id, { status: status as any }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-20 bg-slate-900/60 rounded-2xl border border-slate-800" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-900/60 rounded-xl border border-slate-800" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-72 bg-slate-900/60 rounded-2xl border border-slate-800" />
          <div className="h-72 bg-slate-900/60 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  const tasksSummary = summary?.tasks_summary || { total: 0, completed: 0, pending: 0, overdue: 0, high_priority: 0 };
  const habitsSummary = summary?.habits_summary || { total: 0, completed_today: 0, current_streak_best: 0 };

  return (
    <div className="space-y-6">
      {/* Greeting & Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900/40 border border-indigo-500/20 shadow-xl">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            {summary?.greeting || "Welcome to Personalix OS"}
            <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
              Tier {summary?.productivity_grade || "A"}
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">{summary?.today_date}</p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/daily-plan"
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
          >
            <Clock className="w-3.5 h-3.5" />
            AI Daily Plan
          </Link>
          <Link
            href="/tasks"
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            New Task
          </Link>
        </div>
      </div>

      {/* AI Daily Insight */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-indigo-500/30 flex items-start gap-3.5 shadow-sm">
        <div className="w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
          <Sparkles className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">AI Executive Insight</h3>
          <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">{summary?.ai_daily_insight}</p>
        </div>
      </div>

      {/* Key Metric Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Productivity Score */}
        <div className="p-4 rounded-xl bg-[#111726]/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Productivity Score</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">{summary?.productivity_score || 0}</span>
            <span className="text-xs text-slate-500">/ 100</span>
          </div>
          <p className="text-[10px] text-emerald-400 mt-1 flex items-center gap-1 font-medium">
            <ArrowUpRight className="w-3 h-3" /> +4.2% from last week
          </p>
        </div>

        {/* Task Clearance */}
        <div className="p-4 rounded-xl bg-[#111726]/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Active Tasks</span>
            <CheckCircle2 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">{tasksSummary.pending}</span>
            <span className="text-xs text-slate-500 font-normal">({tasksSummary.completed} done)</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            {tasksSummary.high_priority} critical/high priority items
          </p>
        </div>

        {/* Habit Streaks */}
        <div className="p-4 rounded-xl bg-[#111726]/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Habit Streak</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">{habitsSummary.current_streak_best}</span>
            <span className="text-xs text-slate-500">days record</span>
          </div>
          <p className="text-[10px] text-indigo-300 mt-1">
            {habitsSummary.completed_today} of {habitsSummary.total} habits logged today
          </p>
        </div>

        {/* Active Objectives */}
        <div className="p-4 rounded-xl bg-[#111726]/80 border border-slate-800 hover:border-indigo-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Strategic Goals</span>
            <Target className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-black text-white">{summary?.active_goals_count || 0}</span>
            <span className="text-xs text-slate-500 font-normal">active goals</span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1">
            {summary?.active_projects_count || 0} active tracked projects
          </p>
        </div>
      </div>

      {/* Main Two Column Section: Focus Tasks & Today Schedule */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Focus Priorities (2 cols) */}
        <div className="lg:col-span-2 p-5 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-indigo-400" />
                  Today&apos;s Focus Priorities
                </h2>
                <p className="text-[11px] text-slate-400">High-leverage tasks requiring execution today</p>
              </div>
              <Link href="/tasks" className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">
                View Kanban &rarr;
              </Link>
            </div>

            <div className="space-y-2.5">
              {summary?.today_focus_tasks && summary.today_focus_tasks.length > 0 ? (
                summary.today_focus_tasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-3 rounded-xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700 transition-all flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() =>
                          toggleTaskMutation.mutate({
                            id: task.id,
                            status: task.status === "completed" ? "todo" : "completed",
                          })
                        }
                        className={`w-5 h-5 rounded-md border flex items-center justify-center transition-colors ${
                          task.status === "completed"
                            ? "bg-emerald-500 border-emerald-500 text-white"
                            : "border-slate-700 hover:border-indigo-500"
                        }`}
                      >
                        {task.status === "completed" && <CheckCircle2 className="w-3.5 h-3.5" />}
                      </button>
                      <div>
                        <p
                          className={`text-xs font-medium ${
                            task.status === "completed" ? "line-through text-slate-500" : "text-slate-200"
                          }`}
                        >
                          {task.title}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span
                            className={`text-[10px] px-1.5 py-0.2 rounded uppercase font-mono font-bold ${
                              task.priority === "critical"
                                ? "bg-rose-500/20 text-rose-300"
                                : task.priority === "high"
                                ? "bg-amber-500/20 text-amber-300"
                                : "bg-blue-500/20 text-blue-300"
                            }`}
                          >
                            {task.priority}
                          </span>
                          <span className="text-[10px] text-slate-500 flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {task.estimated_duration}m
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-slate-500 text-xs">
                  All top priorities completed for today! 🎉
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Today's Schedule & Focus Blocks (1 col) */}
        <div className="p-5 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-purple-400" />
                  Today&apos;s Schedule
                </h2>
                <p className="text-[11px] text-slate-400">Time-blocked focus and calendar events</p>
              </div>
              <Link href="/calendar" className="text-xs text-purple-400 hover:text-purple-300 font-medium">
                Calendar &rarr;
              </Link>
            </div>

            <div className="space-y-2.5">
              {summary?.today_events && summary.today_events.length > 0 ? (
                summary.today_events.map((event) => (
                  <div
                    key={event.id}
                    className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start gap-3"
                  >
                    <div
                      className="w-1.5 h-10 rounded-full shrink-0"
                      style={{ backgroundColor: event.color || "#6366f1" }}
                    />
                    <div>
                      <p className="text-xs font-semibold text-slate-200">{event.title}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {new Date(event.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{" "}
                        {new Date(event.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-500 text-xs">
                  No scheduled calendar events for today. Open calendar to add blocks.
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-slate-800/80">
            <Link
              href="/weekly-review"
              className="w-full flex items-center justify-between p-3 rounded-xl bg-purple-950/20 border border-purple-500/20 text-purple-300 hover:bg-purple-950/40 text-xs transition-all"
            >
              <span>Prepare Weekly Review Retrospective</span>
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
