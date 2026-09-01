"use client";

import { useEffect, useState } from "react";
import { Check, X } from "lucide-react";
import { getAvailableVoices } from "@/lib/voice";
import { useVoice } from "@/contexts/VoiceContext";

interface VoiceSettingsProps {
  onClose?: () => void;
}

const LANGUAGES = [
  { code: "en-US", label: "English (US)" },
  { code: "en-IN", label: "English (India / Hinglish)" },
  { code: "hi-IN", label: "Hindi" },
  { code: "en-GB", label: "English (UK)" },
];

export default function VoiceSettings({ onClose }: VoiceSettingsProps) {
  const { settings, updateSettings } = useVoice();
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

  useEffect(() => {
    const load = () => setVoices(getAvailableVoices());
    load();
    if (typeof window !== "undefined") {
      window.speechSynthesis?.addEventListener("voiceschanged", load);
      return () =>
        window.speechSynthesis?.removeEventListener("voiceschanged", load);
    }
  }, []);

  const Slider = ({
    label,
    value,
    min = 0.5,
    max = 2.0,
    step = 0.1,
    field,
    format = (v: number) => v.toFixed(1) + "×",
  }: {
    label: string;
    value: number;
    min?: number;
    max?: number;
    step?: number;
    field: "voice_speed" | "voice_pitch";
    format?: (v: number) => string;
  }) => (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-slate-300">{label}</label>
        <span className="text-xs font-mono text-indigo-400">{format(value)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) =>
          updateSettings({ [field]: parseFloat(e.target.value) })
        }
        className="w-full accent-indigo-500 h-1.5"
      />
    </div>
  );

  const Toggle = ({
    label,
    description,
    field,
  }: {
    label: string;
    description?: string;
    field: keyof typeof settings;
  }) => (
    <div className="flex items-center justify-between gap-3">
      <div>
        <p className="text-xs font-medium text-slate-300">{label}</p>
        {description && (
          <p className="text-[10px] text-slate-500 mt-0.5">{description}</p>
        )}
      </div>
      <button
        onClick={() => updateSettings({ [field]: !settings[field] } as any)}
        className={`relative w-10 h-5 rounded-full transition-colors flex-shrink-0 ${
          settings[field] ? "bg-indigo-600" : "bg-slate-700"
        }`}
      >
        <span
          className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-all ${
            settings[field] ? "left-5" : "left-0.5"
          }`}
        />
      </button>
    </div>
  );

  return (
    <div className="p-5 space-y-5 max-h-[70vh] overflow-y-auto text-xs">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-white">Voice Settings</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* ─ Voice selection ─────────────────────────── */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-slate-300">Voice</label>
        <select
          value={settings.voice_name}
          onChange={(e) => updateSettings({ voice_name: e.target.value })}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-2 text-white text-xs outline-none focus:border-indigo-500"
        >
          <option value="">System Default</option>
          {voices.map((v) => (
            <option key={v.name} value={v.name}>
              {v.name} ({v.lang})
            </option>
          ))}
        </select>
      </div>

      {/* ─ Language ─────────────────────────────────── */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-slate-300">Language / Accent</label>
        <select
          value={settings.language}
          onChange={(e) => updateSettings({ language: e.target.value })}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-2 text-white text-xs outline-none focus:border-indigo-500"
        >
          {LANGUAGES.map((l) => (
            <option key={l.code} value={l.code}>
              {l.label}
            </option>
          ))}
        </select>
      </div>

      {/* ─ Speed & Pitch ───────────────────────────── */}
      <div className="space-y-4 p-3 rounded-xl bg-slate-900/50 border border-slate-800">
        <Slider label="Speed" value={settings.voice_speed} field="voice_speed" />
        <Slider label="Pitch" value={settings.voice_pitch} field="voice_pitch" />
      </div>

      {/* ─ Behaviour toggles ────────────────────────── */}
      <div className="space-y-3 p-3 rounded-xl bg-slate-900/50 border border-slate-800">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Behaviour</p>
        <Toggle label="Auto-Speak Responses" field="auto_speak" />
        <Toggle
          label="Proactive Mode"
          description="AI surfaces upcoming events & overdue tasks"
          field="proactive_mode"
        />
      </div>

      {/* ─ Privacy ──────────────────────────────────── */}
      <div className="space-y-3 p-3 rounded-xl bg-slate-900/50 border border-slate-800">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Privacy</p>
        <Toggle
          label="Save Voice Transcripts"
          description="Store voice conversation text in history"
          field="save_transcripts"
        />
        <Toggle
          label="Confirm Destructive Actions"
          description="Require confirmation before deleting / wiping data"
          field="confirm_destructive_actions"
        />
      </div>

      <p className="text-[10px] text-slate-600 text-center">
        Microphone is only accessed while actively listening. A visual indicator is always shown.
      </p>
    </div>
  );
}
