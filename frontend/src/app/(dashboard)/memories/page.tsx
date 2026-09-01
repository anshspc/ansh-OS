"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Brain,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { AIMemory } from "@/lib/types";

export default function MemoriesPage() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [content, setContent] = useState("");
  const [category, setCategory] = useState<AIMemory["category"]>("preference");

  const { data: memories = [], isLoading } = useQuery({
    queryKey: ["ai-memories"],
    queryFn: () => api.getMemories(),
  });

  const createMemoryMutation = useMutation({
    mutationFn: (newMem: Partial<AIMemory>) => api.createMemory(newMem),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-memories"] });
      setIsCreateOpen(false);
      setContent("");
    },
  });

  const deleteMemoryMutation = useMutation({
    mutationFn: (id: string) => api.deleteMemory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-memories"] });
    },
  });

  const grouped = memories.reduce((acc, mem) => {
    acc[mem.category] = [...(acc[mem.category] || []), mem];
    return acc;
  }, {} as Record<string, AIMemory[]>);

  const categoryColors: Record<string, string> = {
    preference: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    goal: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    project: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    fact: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    behavioral_pattern: "bg-rose-500/20 text-rose-300 border-rose-500/30",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Brain className="w-6 h-6 text-purple-400" />
            AI Long-Term Memory Graph
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Contextual knowledge extracted across conversations — makes the AI assistant increasingly personalized
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Pin Memory
        </button>
      </div>

      {/* Memory Breakdown by Category */}
      {Object.entries(grouped).map(([cat, mems]) => (
        <div key={cat} className="space-y-3">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            {cat.replace("_", " ")} ({mems.length})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {mems.map((mem) => (
              <div
                key={mem.id}
                className={`p-4 rounded-xl border flex items-start justify-between gap-3 ${
                  categoryColors[mem.category] || "bg-slate-900/60 text-slate-300 border-slate-800"
                }`}
              >
                <div>
                  <p className="text-xs font-semibold leading-relaxed">{mem.content}</p>
                  <p className="text-[10px] mt-1.5 opacity-70 font-mono">
                    Confidence: {(mem.confidence * 100).toFixed(0)}% • Source: {mem.source}
                  </p>
                </div>
                <button
                  onClick={() => deleteMemoryMutation.mutate(mem.id)}
                  className="text-slate-400 hover:text-rose-400 shrink-0 p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}

      {memories.length === 0 && (
        <div className="p-12 rounded-2xl bg-[#111726]/60 border border-slate-800 text-center space-y-3">
          <Brain className="w-10 h-10 text-slate-600 mx-auto" />
          <p className="text-xs text-slate-400">
            No memories yet. Chat with the AI Assistant to auto-extract memories, or manually pin important facts above.
          </p>
        </div>
      )}

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#111726] border border-slate-800 rounded-2xl w-full max-w-md shadow-2xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-white">Pin Memory Fragment</h2>
              <button onClick={() => setIsCreateOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Memory Content *</label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={4}
                  placeholder="e.g. User prefers working with TypeScript. Always uses async/await over callbacks."
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value as any)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white outline-none"
                >
                  <option value="preference">Preference</option>
                  <option value="goal">Goal</option>
                  <option value="project">Project</option>
                  <option value="fact">Fact</option>
                  <option value="behavioral_pattern">Behavioral Pattern</option>
                </select>
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
                  if (content.trim()) {
                    createMemoryMutation.mutate({ content, category, source: "manual" });
                  }
                }}
                disabled={!content.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold"
              >
                Pin Memory
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
