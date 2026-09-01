"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  CheckCircle2,
  Flame,
  Plus,
  Trash2,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import { format, subDays } from "date-fns";
import { api } from "@/lib/api";
import { Habit } from "@/lib/types";

export default function HabitsPage() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [frequency, setFrequency] = useState<"daily" | "weekly">("daily");
  const [reminderTime, setReminderTime] = useState("08:00");
  const [color, setColor] = useState("#8b5cf6");

  const { data: habits = [], isLoading } = useQuery({
    queryKey: ["habits"],
    queryFn: () => api.getHabits(),
  });

  const { data: heatmapData = {} } = useQuery({
    queryKey: ["habit-heatmap"],
    queryFn: () => api.getHabitHeatmap(365),
  });

  const logHabitMutation = useMutation({
    mutationFn: ({ id, date, completed }: { id: string; date: string; completed: boolean }) =>
      api.logHabit(id, date, completed),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      queryClient.invalidateQueries({ queryKey: ["habit-heatmap"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const createHabitMutation = useMutation({
    mutationFn: (newHabit: Partial<Habit>) => api.createHabit(newHabit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
      setIsCreateOpen(false);
      setTitle("");
      setDescription("");
    },
  });

  const deleteHabitMutation = useMutation({
    mutationFn: (id: string) => api.deleteHabit(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["habits"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });

  const todayStr = format(new Date(), "yyyy-MM-dd");

  // Generate 52 weeks (364 days) of grid cells
  const days = Array.from({ length: 364 }).map((_, idx) => {
    const d = subDays(new Date(), 363 - idx);
    const dStr = format(d, "yyyy-MM-dd");
    const count = heatmapData[dStr] || 0;
    return { date: dStr, count };
  });

  const getHeatmapColor = (count: number) => {
    if (count === 0) return "bg-slate-900 border-slate-800/80";
    if (count === 1) return "bg-indigo-950 border-indigo-800 text-indigo-200";
    if (count === 2) return "bg-indigo-800 border-indigo-700 text-white";
    if (count === 3) return "bg-indigo-600 border-indigo-500 text-white";
    return "bg-purple-500 border-purple-400 text-white shadow-sm shadow-purple-500/30";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Habits & Consistency Engine</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Build compounding momentum with daily check-ins and visual streak analytics
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Track Habit
        </button>
      </div>

      {/* 365-Day Interactive Heatmap */}
      <div className="p-5 rounded-2xl bg-[#111726]/80 border border-slate-800 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-rose-400" />
            <h2 className="text-xs font-bold text-white uppercase tracking-wider">
              Yearly Habit Consistency Heatmap (Last 365 Days)
            </h2>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-slate-400">
            <span>Less</span>
            <div className="flex gap-1">
              <span className="w-2.5 h-2.5 rounded-sm bg-slate-900 border border-slate-800" />
              <span className="w-2.5 h-2.5 rounded-sm bg-indigo-950 border border-indigo-800" />
              <span className="w-2.5 h-2.5 rounded-sm bg-indigo-800 border border-indigo-700" />
              <span className="w-2.5 h-2.5 rounded-sm bg-indigo-600 border border-indigo-500" />
              <span className="w-2.5 h-2.5 rounded-sm bg-purple-500 border border-purple-400" />
            </div>
            <span>More</span>
          </div>
        </div>

        {/* CSS Heatmap Grid: 52 columns, 7 rows */}
        <div className="overflow-x-auto pb-2">
          <div className="grid grid-flow-col grid-rows-7 gap-1 min-w-[700px]">
            {days.map((d, i) => (
              <div
                key={i}
                title={`${d.date}: ${d.count} habits completed`}
                className={`w-3 h-3 rounded-sm border transition-all hover:scale-125 hover:z-10 ${getHeatmapColor(
                  d.count
                )}`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Habits List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {habits.map((habit) => (
          <div
            key={habit.id}
            className="p-5 rounded-2xl bg-[#111726]/80 border border-slate-800 hover:border-slate-700 transition-all flex items-start justify-between gap-4 group shadow-sm"
          >
            <div className="flex items-start gap-3.5">
              <button
                onClick={() =>
                  logHabitMutation.mutate({
                    id: habit.id,
                    date: todayStr,
                    completed: !habit.today_completed,
                  })
                }
                className={`w-9 h-9 rounded-xl border flex items-center justify-center transition-all ${
                  habit.today_completed
                    ? "bg-emerald-500 border-emerald-400 text-white shadow-lg shadow-emerald-500/20 scale-105"
                    : "border-slate-700 hover:border-indigo-500 text-slate-500 hover:text-indigo-400 bg-slate-900/60"
                }`}
              >
                <Check className={`w-4 h-4 ${habit.today_completed ? "stroke-[3]" : ""}`} />
              </button>

              <div>
                <h3
                  className={`text-sm font-bold ${
                    habit.today_completed ? "text-slate-200" : "text-white"
                  }`}
                >
                  {habit.title}
                </h3>
                {habit.description && (
                  <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{habit.description}</p>
                )}

                <div className="flex items-center gap-3 mt-3 text-xs">
                  <span className="flex items-center gap-1 text-rose-400 font-bold font-mono">
                    <Flame className="w-3.5 h-3.5" />
                    {habit.streak_count} day streak
                  </span>
                  <span className="text-slate-500">Best: {habit.best_streak}d</span>
                  <span className="text-slate-400 font-mono">
                    {habit.completion_rate_30d}% (30d)
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => deleteHabitMutation.mutate(habit.id)}
              className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-rose-400 transition-opacity p-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      {/* Create Habit Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111726] border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white">Track New Habit</h2>
              <button onClick={() => setIsCreateOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Habit Name *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Read 1 Research Paper"
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                  placeholder="Why this routine matters..."
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Reminder Time</label>
                  <input
                    type="time"
                    value={reminderTime}
                    onChange={(e) => setReminderTime(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Color</label>
                  <input
                    type="color"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="w-full h-9 bg-slate-900 border border-slate-700 rounded-lg p-1 outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                onClick={() => setIsCreateOpen(false)}
                className="px-4 py-2 rounded-xl text-slate-400 hover:text-white text-xs"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (title.trim()) {
                    createHabitMutation.mutate({
                      title,
                      description,
                      frequency,
                      reminder_time: reminderTime,
                      color,
                    });
                  }
                }}
                disabled={!title.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold"
              >
                Save Habit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
