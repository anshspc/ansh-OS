"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  BookOpen,
  Calendar,
  CheckSquare,
  Clock,
  Compass,
  FileText,
  Flame,
  FolderKanban,
  LayoutDashboard,
  Search,
  Sparkles,
  Target,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { SearchResultItem } from "@/lib/types";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenAI: (prompt?: string) => void;
}

export default function CommandPalette({ isOpen, onClose, onOpenAI }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // Open
        }
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await api.searchKnowledge(query, 6);
        setResults(data.results || []);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  if (!isOpen) return null;

  const quickNav = [
    { label: "Go to Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Go to Tasks (Kanban)", href: "/tasks", icon: CheckSquare },
    { label: "Go to Projects", href: "/projects", icon: FolderKanban },
    { label: "Go to Goals", href: "/goals", icon: Target },
    { label: "Go to Habits Heatmap", href: "/habits", icon: Flame },
    { label: "Go to Notes & Docs", href: "/notes", icon: BookOpen },
    { label: "Go to AI Daily Planner", href: "/daily-plan", icon: Clock },
    { label: "Go to Weekly AI Review", href: "/weekly-review", icon: Compass },
  ];

  const handleSelectNav = (href: string) => {
    router.push(href);
    onClose();
  };

  const handleAskAI = () => {
    onClose();
    onOpenAI(query);
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-start justify-center pt-20 p-4 animate-in fade-in duration-150">
      <div className="bg-[#111726] border border-slate-700/80 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Search Header */}
        <div className="flex items-center px-4 py-3 border-b border-slate-800 gap-3">
          <Search className="w-5 h-5 text-indigo-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across OS entities, documents, or ask AI..."
            autoFocus
            className="bg-transparent border-none outline-none text-slate-100 text-sm w-full placeholder-slate-500"
          />
          {query && (
            <button onClick={() => setQuery("")} className="text-slate-500 hover:text-slate-300">
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="px-2 py-0.5 text-[11px] font-mono bg-slate-800 text-slate-400 rounded border border-slate-700">
            ESC
          </kbd>
        </div>

        {/* Content Body */}
        <div className="p-3 max-h-[60vh] overflow-y-auto space-y-4">
          {/* AI Prompt action if query exists */}
          {query && (
            <div className="p-1">
              <button
                onClick={handleAskAI}
                className="w-full flex items-center justify-between p-3 rounded-xl bg-indigo-600/10 hover:bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 text-xs font-medium transition-all group"
              >
                <span className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Ask AI Assistant: <span className="font-semibold text-white truncate">&quot;{query}&quot;</span>
                </span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
          )}

          {/* Search Results */}
          {results.length > 0 && (
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-2 mb-1.5">
                Search Results ({results.length})
              </p>
              <div className="space-y-1">
                {results.map((res) => (
                  <div
                    key={`${res.type}-${res.id}`}
                    onClick={() => {
                      if (res.type === "task") handleSelectNav("/tasks");
                      else if (res.type === "note") handleSelectNav("/notes");
                      else if (res.type === "document") handleSelectNav("/documents");
                      else if (res.type === "project") handleSelectNav("/projects");
                    }}
                    className="p-2.5 rounded-lg hover:bg-slate-800/70 border border-transparent hover:border-slate-700/60 cursor-pointer transition-all flex items-start justify-between group"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 uppercase font-mono">
                          {res.type}
                        </span>
                        <span className="text-xs font-medium text-slate-200 group-hover:text-indigo-300 transition-colors">
                          {res.title}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 line-clamp-1">
                        {res.snippet}
                      </p>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      {(res.score * 100).toFixed(0)}% match
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Navigation Defaults */}
          {!query && (
            <div>
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-2 mb-1.5">
                Quick Navigation
              </p>
              <div className="grid grid-cols-2 gap-1.5">
                {quickNav.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={item.href}
                      onClick={() => handleSelectNav(item.href)}
                      className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-800/60 text-slate-300 text-xs transition-all text-left group border border-transparent hover:border-slate-700/40"
                    >
                      <Icon className="w-4 h-4 text-slate-400 group-hover:text-indigo-400 transition-colors" />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
