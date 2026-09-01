"use client";

import { Bell, Mic, Plus, Search, Sparkles } from "lucide-react";
import { format } from "date-fns";
import { useVoice } from "@/contexts/VoiceContext";
import { VoiceState, VOICE_STATE_COLORS, VOICE_STATE_LABELS } from "@/lib/voice";

interface HeaderProps {
  onOpenCommand: () => void;
  onOpenAI: () => void;
  onQuickTask?: () => void;
}

export default function Header({ onOpenCommand, onOpenAI, onQuickTask }: HeaderProps) {
  const todayStr = format(new Date(), "EEEE, MMMM do");
  const { voiceState, isActive, openVoice } = useVoice();
  const isListening = voiceState === VoiceState.LISTENING;
  const voiceColor = VOICE_STATE_COLORS[voiceState];

  return (
    <header className="h-14 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-md sticky top-0 z-20 px-6 flex items-center justify-between">
      {/* Global Search Bar */}
      <div className="flex items-center gap-4 w-96">
        <button
          onClick={onOpenCommand}
          className="w-full flex items-center justify-between px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 hover:border-slate-700 text-slate-400 text-xs transition-all shadow-inner group"
        >
          <span className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-400" />
            Search tasks, notes, documents, or ask AI...
          </span>
          <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-slate-800 text-slate-400 rounded border border-slate-700">
            Ctrl+K
          </kbd>
        </button>
      </div>

      {/* Center Date Display */}
      <div className="hidden md:flex items-center text-xs text-slate-400 font-medium gap-3">
        <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-ping" />
        {todayStr}

        {/* Voice status indicator when active */}
        {isActive && (
          <span
            className="flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[10px] font-semibold"
            style={{
              color: voiceColor,
              borderColor: `${voiceColor}44`,
              backgroundColor: `${voiceColor}11`,
            }}
          >
            <Mic className={`w-3 h-3 ${isListening ? "animate-pulse" : ""}`} />
            {VOICE_STATE_LABELS[voiceState]}
          </span>
        )}
      </div>

      {/* Right Quick Actions */}
      <div className="flex items-center gap-2.5">
        {/* Voice quick trigger */}
        <button
          onClick={openVoice}
          title="Personalix Voice (Ctrl+Space)"
          className={`relative p-1.5 rounded-lg border text-xs transition-all ${
            isListening
              ? "bg-emerald-600/20 border-emerald-500/40 text-emerald-400"
              : isActive
              ? "bg-purple-600/20 border-purple-500/40 text-purple-300"
              : "bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300 hover:border-purple-500/30"
          }`}
        >
          <Mic className={`w-3.5 h-3.5 ${isListening ? "animate-pulse" : ""}`} />
          {isListening && (
            <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
          )}
        </button>

        <button
          onClick={onOpenAI}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 text-xs font-medium transition-all shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Ask Personalix</span>
        </button>
      </div>
    </header>
  );
}
