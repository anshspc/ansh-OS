"use client";

import { useEffect, useState } from "react";
import {
  Check,
  Mic,
  MicOff,
  Settings,
  Square,
  Volume2,
  VolumeX,
  X,
} from "lucide-react";
import { VoiceState, VOICE_STATE_COLORS, VOICE_STATE_LABELS } from "@/lib/voice";
import { useVoice } from "@/contexts/VoiceContext";
import VoiceOrb from "./VoiceOrb";
import VoiceWaveform from "./VoiceWaveform";
import VoiceSettings from "./VoiceSettings";

export default function VoiceOverlay() {
  const {
    voiceState,
    isSupported,
    isActive,
    transcript,
    lastResponse,
    messages,
    settings,
    pendingConfirmation,
    closeVoice,
    startListening,
    stopListening,
    stopSpeaking,
    confirmAction,
    updateSettings,
  } = useVoice();

  const [showSettings, setShowSettings] = useState(false);

  // Play welcome greeting when overlay first opens
  const { speak } = useVoice();
  useEffect(() => {
    if (isActive && voiceState === VoiceState.IDLE && messages.length === 0) {
      const hour = new Date().getHours();
      const greeting =
        hour < 12
          ? "Good morning."
          : hour < 17
          ? "Good afternoon."
          : "Good evening.";
      setTimeout(() => {
        speak(
          `${greeting} I'm Personalix Voice. Press the orb or say what you'd like to do.`
        );
      }, 400);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive]);

  if (!isActive) return null;

  const stateColor = VOICE_STATE_COLORS[voiceState];
  const stateLabel = VOICE_STATE_LABELS[voiceState];

  const canListen =
    voiceState === VoiceState.IDLE || voiceState === VoiceState.SPEAKING;
  const isListening = voiceState === VoiceState.LISTENING;
  const isSpeaking = voiceState === VoiceState.SPEAKING;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center">
      {/* Dark backdrop */}
      <div
        className="absolute inset-0 bg-black/75 backdrop-blur-md"
        onClick={closeVoice}
      />

      {/* Panel */}
      <div className="relative w-full max-w-md mx-4 bg-[#0d121f]/95 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col">

        {/* Header bar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-800/80 bg-[#111726]/60">
          <div className="flex items-center gap-2">
            <div
              className="w-2 h-2 rounded-full animate-pulse"
              style={{ backgroundColor: stateColor }}
            />
            <span className="text-xs font-bold text-white tracking-wider uppercase">
              Personalix Voice
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setShowSettings((s) => !s)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
              title="Voice settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={closeVoice}
              className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
              title="Close voice"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Settings panel inline */}
        {showSettings && (
          <div className="border-b border-slate-800">
            <VoiceSettings onClose={() => setShowSettings(false)} />
          </div>
        )}

        {/* Main voice display */}
        <div className="flex flex-col items-center justify-center py-10 px-6 gap-6">
          {/* Orb — clickable to toggle listening */}
          <VoiceOrb
            state={voiceState}
            size={120}
            onClick={() => {
              if (isListening) stopListening();
              else if (isSpeaking) stopSpeaking();
              else startListening();
            }}
          />

          {/* Waveform */}
          <VoiceWaveform state={voiceState} barCount={24} height={52} />

          {/* State label */}
          <div className="text-center space-y-1">
            <p
              className="text-sm font-bold tracking-widest uppercase transition-all duration-300"
              style={{ color: stateColor }}
            >
              {stateLabel}
            </p>

            {/* Live transcript */}
            {(voiceState === VoiceState.LISTENING || transcript) && (
              <p className="text-xs text-slate-300 max-w-xs text-center leading-relaxed mt-1 min-h-[36px]">
                {transcript
                  ? `"${transcript}"`
                  : "Say something..."}
              </p>
            )}

            {/* Last AI response */}
            {lastResponse &&
              voiceState !== VoiceState.LISTENING && (
                <p className="text-xs text-slate-400 max-w-xs text-center leading-relaxed mt-2 italic">
                  {lastResponse.length > 180
                    ? lastResponse.slice(0, 180) + "…"
                    : lastResponse}
                </p>
              )}
          </div>

          {/* Confirmation prompt */}
          {pendingConfirmation && (
            <div className="w-full p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 space-y-3">
              <p className="text-xs text-amber-200 text-center">
                {pendingConfirmation.prompt}
              </p>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => confirmAction(true)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm transition-all"
                >
                  <Check className="w-3.5 h-3.5" /> Yes, proceed
                </button>
                <button
                  onClick={() => confirmAction(false)}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-all"
                >
                  <X className="w-3.5 h-3.5" /> Cancel
                </button>
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-3 mt-2">
            {/* Main listen / stop button */}
            <button
              disabled={voiceState === VoiceState.PROCESSING || voiceState === VoiceState.EXECUTING}
              onClick={() => {
                if (isListening) stopListening();
                else if (isSpeaking) stopSpeaking();
                else startListening();
              }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-xs font-bold shadow-lg transition-all disabled:opacity-40"
              style={{
                backgroundColor: stateColor,
                boxShadow: `0 4px 20px ${stateColor}40`,
              }}
            >
              {isListening ? (
                <>
                  <Square className="w-3.5 h-3.5" fill="white" /> Stop
                </>
              ) : isSpeaking ? (
                <>
                  <VolumeX className="w-3.5 h-3.5" /> Interrupt
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5" /> Speak
                </>
              )}
            </button>

            {/* Auto-speak toggle */}
            <button
              onClick={() => updateSettings({ auto_speak: !settings.auto_speak })}
              className={`p-2.5 rounded-xl border text-xs transition-all ${
                settings.auto_speak
                  ? "bg-indigo-600/20 border-indigo-500/40 text-indigo-300"
                  : "bg-slate-900 border-slate-700 text-slate-400"
              }`}
              title={settings.auto_speak ? "Auto-speak ON" : "Auto-speak OFF"}
            >
              {settings.auto_speak ? (
                <Volume2 className="w-4 h-4" />
              ) : (
                <VolumeX className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Hotkey hint */}
          <p className="text-[10px] text-slate-600 mt-1">
            <kbd className="px-1.5 py-0.5 bg-slate-900 rounded border border-slate-700 font-mono">
              Ctrl+Space
            </kbd>{" "}
            to toggle listening anywhere
          </p>
        </div>

        {/* Browser not supported message */}
        {!isSupported && (
          <div className="px-5 pb-4 text-center">
            <p className="text-xs text-amber-400 bg-amber-950/30 border border-amber-500/20 rounded-lg px-3 py-2">
              Voice requires Chrome, Edge, or Safari. Firefox does not support the
              Web Speech API.
            </p>
          </div>
        )}

        {/* Mic indicator */}
        {isListening && (
          <div className="absolute top-3 right-16 flex items-center gap-1.5 text-[10px] text-emerald-400 font-mono bg-emerald-950/50 border border-emerald-500/30 px-2 py-1 rounded-lg">
            <Mic className="w-3 h-3 animate-pulse" />
            Mic active
          </div>
        )}
      </div>
    </div>
  );
}
