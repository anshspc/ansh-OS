"use client";

import { Mic } from "lucide-react";
import { useVoice } from "@/contexts/VoiceContext";
import { VoiceState, VOICE_STATE_COLORS } from "@/lib/voice";

/**
 * Compact voice conversation history inside the voice overlay or sidebar.
 */
export default function VoiceConversation() {
  const { messages } = useVoice();

  if (messages.length === 0) return null;

  return (
    <div className="space-y-2 max-h-48 overflow-y-auto px-1">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex gap-2 text-xs ${
            msg.role === "user" ? "flex-row-reverse" : "flex-row"
          }`}
        >
          {/* Avatar */}
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-[10px] font-bold ${
              msg.role === "user"
                ? "bg-indigo-600 text-white"
                : "bg-purple-700 text-white"
            }`}
          >
            {msg.role === "user" ? "U" : "P"}
          </div>

          {/* Bubble */}
          <div
            className={`max-w-[75%] rounded-xl px-3 py-2 leading-relaxed ${
              msg.role === "user"
                ? "bg-indigo-600/20 text-slate-200 border border-indigo-600/30"
                : "bg-slate-800/70 text-slate-300 border border-slate-700/50"
            }`}
          >
            {/* Voice badge */}
            {msg.input_type === "voice" && (
              <span className="inline-flex items-center gap-0.5 text-[9px] text-indigo-400 mb-0.5">
                <Mic className="w-2.5 h-2.5" /> voice
              </span>
            )}
            <p>{msg.content}</p>

            {/* Tool call badges */}
            {msg.tool_calls && msg.tool_calls.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-1.5">
                {msg.tool_calls.map((tc: any, i: number) => (
                  <span
                    key={i}
                    className="px-1.5 py-0.5 rounded bg-cyan-950/50 text-cyan-400 border border-cyan-600/30 text-[9px] font-mono"
                  >
                    ⚡ {tc.name}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
