"use client";

import { VoiceState, VOICE_STATE_COLORS } from "@/lib/voice";

interface VoiceOrbProps {
  state: VoiceState;
  size?: number;
  onClick?: () => void;
}

export default function VoiceOrb({ state, size = 96, onClick }: VoiceOrbProps) {
  const color = VOICE_STATE_COLORS[state];
  const half = size / 2;

  // State-specific animation class
  const animClass = {
    [VoiceState.IDLE]: "animate-pulse",
    [VoiceState.LISTENING]: "animate-ping-slow",
    [VoiceState.PROCESSING]: "animate-spin-slow",
    [VoiceState.EXECUTING]: "animate-bounce",
    [VoiceState.SPEAKING]: "animate-pulse-fast",
  }[state];

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Voice assistant — ${state.toLowerCase()}`}
      onClick={onClick}
      onKeyDown={(e) => e.key === "Enter" && onClick?.()}
      className="relative flex items-center justify-center cursor-pointer select-none focus:outline-none"
      style={{ width: size, height: size }}
    >
      {/* Outer ring — state pulse */}
      <div
        className={`absolute rounded-full opacity-20 ${animClass}`}
        style={{
          width: size,
          height: size,
          backgroundColor: color,
        }}
      />

      {/* Mid ring */}
      <div
        className="absolute rounded-full opacity-30"
        style={{
          width: size * 0.75,
          height: size * 0.75,
          backgroundColor: color,
          animation: state === VoiceState.LISTENING
            ? "orbMid 1.2s ease-in-out infinite alternate"
            : state === VoiceState.SPEAKING
            ? "orbMid 0.6s ease-in-out infinite alternate"
            : "none",
        }}
      />

      {/* Core orb */}
      <div
        className="relative rounded-full flex items-center justify-center shadow-2xl transition-all duration-300"
        style={{
          width: size * 0.55,
          height: size * 0.55,
          background: `radial-gradient(circle at 35% 35%, ${color}cc, ${color}88)`,
          boxShadow: `0 0 ${size * 0.3}px ${color}55, inset 0 1px 0 rgba(255,255,255,0.2)`,
        }}
      >
        {/* Inner glyph */}
        <svg
          width={size * 0.22}
          height={size * 0.22}
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          {state === VoiceState.LISTENING ? (
            // Microphone on
            <>
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </>
          ) : state === VoiceState.SPEAKING ? (
            // Sound waves
            <>
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            </>
          ) : state === VoiceState.PROCESSING || state === VoiceState.EXECUTING ? (
            // Spinning dots / sparkle
            <>
              <circle cx="12" cy="12" r="3" />
              <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" />
            </>
          ) : (
            // IDLE — mic off
            <>
              <line x1="1" y1="1" x2="23" y2="23" />
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
              <line x1="12" y1="19" x2="12" y2="23" />
              <line x1="8" y1="23" x2="16" y2="23" />
            </>
          )}
        </svg>
      </div>

      {/* CSS keyframes injected inline */}
      <style>{`
        @keyframes orbMid {
          from { transform: scale(0.9); opacity: 0.25; }
          to   { transform: scale(1.05); opacity: 0.4; }
        }
        .animate-ping-slow {
          animation: ping 1.4s cubic-bezier(0, 0, 0.2, 1) infinite;
        }
        .animate-spin-slow {
          animation: spin 2s linear infinite;
        }
        .animate-pulse-fast {
          animation: pulse 0.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
}
