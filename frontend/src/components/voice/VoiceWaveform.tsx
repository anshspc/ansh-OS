"use client";

import { useEffect, useRef } from "react";
import { VoiceState, VOICE_STATE_COLORS } from "@/lib/voice";

interface VoiceWaveformProps {
  state: VoiceState;
  barCount?: number;
  height?: number;
}

export default function VoiceWaveform({
  state,
  barCount = 20,
  height = 48,
}: VoiceWaveformProps) {
  const color = VOICE_STATE_COLORS[state];
  const bars = Array.from({ length: barCount });

  const isAnimating =
    state === VoiceState.LISTENING || state === VoiceState.SPEAKING;

  return (
    <div
      className="flex items-center justify-center gap-[3px]"
      style={{ height }}
      aria-hidden="true"
    >
      {bars.map((_, i) => {
        // Create a natural-looking wave by offsetting animation delays
        const delay = `${(i / barCount) * 0.6}s`;
        const minH = height * 0.12;
        const maxH = height * (0.4 + Math.sin((i / barCount) * Math.PI) * 0.5);

        return (
          <div
            key={i}
            className="rounded-full transition-all"
            style={{
              width: 3,
              minHeight: minH,
              height: isAnimating ? maxH : minH,
              backgroundColor: color,
              opacity: isAnimating ? 0.85 : 0.25,
              animation: isAnimating
                ? `waveBar 0.7s ease-in-out ${delay} infinite alternate`
                : "none",
            }}
          />
        );
      })}

      <style>{`
        @keyframes waveBar {
          from { transform: scaleY(0.3); opacity: 0.4; }
          to   { transform: scaleY(1);   opacity: 0.9; }
        }
      `}</style>
    </div>
  );
}
