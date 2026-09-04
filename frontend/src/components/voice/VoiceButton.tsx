"use client";

import { Mic, MicOff } from "lucide-react";
import { useVoice } from "@/contexts/VoiceContext";
import { VoiceState, VOICE_STATE_COLORS } from "@/lib/voice";

interface VoiceButtonProps {
  className?: string;
}

/**
 * Floating voice activation button — rendered in the dashboard layout
 * so it appears on every authenticated page.
 */
export default function VoiceButton({ className = "" }: VoiceButtonProps) {
  const { voiceState, isActive, isSupported, openVoice } = useVoice();

  const isListening = voiceState === VoiceState.LISTENING;
  const isSpeaking = voiceState === VoiceState.SPEAKING;
  const color = isActive ? VOICE_STATE_COLORS[voiceState] : "#6366f1";

  return (
    <button
      onClick={openVoice}
      title="Personalix Voice (Ctrl+Space)"
      aria-label="Open Personalix Voice"
      className={`group relative flex items-center justify-center w-12 h-12 rounded-2xl transition-all duration-200 shadow-xl hover:scale-110 active:scale-95 ${className}`}
      style={{
        background: isActive
          ? `linear-gradient(135deg, ${color}cc, ${color}88)`
          : "linear-gradient(135deg, #6366f1cc, #8b5cf688)",
        boxShadow: `0 4px 24px ${color}44`,
      }}
    >
      {/* Active pulse ring */}
      {isActive && (
        <span
          className="absolute inset-0 rounded-2xl animate-ping opacity-30"
          style={{ backgroundColor: color }}
        />
      )}

      {isListening ? (
        <Mic className="w-5 h-5 text-white animate-pulse" />
      ) : (
        <Mic className="w-5 h-5 text-white" />
      )}

      {/* State dot */}
      {isActive && (
        <span
          className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full border border-[#0d121f]"
          style={{ backgroundColor: color }}
        />
      )}

      {/* Tooltip */}
      <span className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 whitespace-nowrap bg-slate-900 border border-slate-700 text-white text-[10px] font-semibold px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        Personalix Voice
        <span className="ml-1.5 text-slate-500 font-mono">Ctrl+Space</span>
      </span>
    </button>
  );
}
