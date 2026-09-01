"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  BarChart3,
  BookOpen,
  Brain,
  Calendar,
  CheckSquare,
  Clock,
  Compass,
  FileText,
  Flame,
  FolderKanban,
  Layers,
  LayoutDashboard,
  LogOut,
  Mic,
  Sparkles,
  Target,
  UserCheck,
} from "lucide-react";
import { api } from "@/lib/api";
import { useVoice } from "@/contexts/VoiceContext";
import { VoiceState, VOICE_STATE_COLORS } from "@/lib/voice";

interface SidebarProps {
  onOpenAI: () => void;
  onOpenCommand: () => void;
}

export default function Sidebar({ onOpenAI, onOpenCommand }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { voiceState, isActive, openVoice } = useVoice();
  const voiceColor = VOICE_STATE_COLORS[voiceState];

  const navItems = [
    { label: "Command Center", href: "/dashboard", icon: LayoutDashboard },
    { label: "Tasks & Kanban", href: "/tasks", icon: CheckSquare },
    { label: "Projects", href: "/projects", icon: FolderKanban },
    { label: "Goals & Milestones", href: "/goals", icon: Target },
    { label: "Habits & Streaks", href: "/habits", icon: Flame },
    { label: "Notes & Docs", href: "/notes", icon: BookOpen },
    { label: "Knowledge RAG", href: "/documents", icon: FileText },
    { label: "Calendar & Focus", href: "/calendar", icon: Calendar },
    { label: "AI Daily Planner", href: "/daily-plan", icon: Clock },
    { label: "Weekly AI Review", href: "/weekly-review", icon: Compass },
    { label: "Analytics & Score", href: "/analytics", icon: BarChart3 },
    { label: "AI Long-Term Memory", href: "/memories", icon: Brain },
  ];

  const handleLogout = () => {
    api.clearToken();
    router.push("/login");
  };

  return (
    <aside className="w-64 bg-[#0d121f] border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div>
        <div className="p-4 flex items-center justify-between border-b border-slate-800/60">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-4 h-4 text-white animate-pulse" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                Personalix <span className="text-xs px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono">OS</span>
              </span>
            </div>
          </Link>
        </div>

        {/* Quick AI Trigger Banner */}
        <div className="p-3 space-y-1.5">
          <button
            onClick={onOpenAI}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-gradient-to-r from-indigo-900/40 via-purple-900/30 to-pink-900/20 border border-indigo-500/30 hover:border-indigo-500/60 text-indigo-200 transition-all text-xs font-medium group shadow-sm hover:shadow-indigo-500/10"
          >
            <span className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400 group-hover:rotate-12 transition-transform" />
              AI Assistant
            </span>
            <span className="text-[10px] bg-indigo-500/30 text-indigo-300 px-1.5 py-0.5 rounded font-mono">
              Ctrl+J
            </span>
          </button>

          {/* Personalix Voice trigger */}
          <button
            onClick={openVoice}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-gradient-to-r from-purple-900/30 to-violet-900/20 border border-purple-500/30 hover:border-purple-500/60 text-purple-200 transition-all text-xs font-medium group shadow-sm"
            style={isActive ? { borderColor: `${voiceColor}55` } : {}}
          >
            <span className="flex items-center gap-2">
              <Mic
                className={`w-3.5 h-3.5 ${isActive ? "text-emerald-400 animate-pulse" : "text-purple-400"}`}
              />
              Personalix Voice
            </span>
            <span className="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded font-mono">
              Ctrl+Space
            </span>
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="px-2 space-y-1 overflow-y-auto max-h-[calc(100vh-250px)] py-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-slate-500"}`} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-800/60">
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-7 h-7 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-xs font-bold text-indigo-300">
              AM
            </div>
            <div className="truncate">
              <p className="text-xs font-medium text-slate-200 truncate">Alex Mercer</p>
              <p className="text-[10px] text-slate-500 truncate">demo@personalix.os</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="p-1.5 text-slate-500 hover:text-rose-400 rounded-md hover:bg-slate-800 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
