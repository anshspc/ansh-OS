/**
 * Voice subsystem type definitions for Personalix Voice.
 */

export enum VoiceState {
  IDLE = "IDLE",
  LISTENING = "LISTENING",
  PROCESSING = "PROCESSING",
  EXECUTING = "EXECUTING",
  SPEAKING = "SPEAKING",
}

export interface VoiceSettings {
  voice_name: string;
  voice_speed: number;       // 0.5 – 2.0
  voice_pitch: number;       // 0.5 – 2.0
  auto_speak: boolean;
  language: string;          // en-US | hi-IN | en-IN | en-GB
  proactive_mode: boolean;
  proactive_interval_minutes: number;
  save_transcripts: boolean;
  voice_history_enabled: boolean;
  wake_word_enabled: boolean;
  confirm_destructive_actions: boolean;
}

export const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  voice_name: "",
  voice_speed: 1.0,
  voice_pitch: 1.0,
  auto_speak: true,
  language: "en-US",
  proactive_mode: false,
  proactive_interval_minutes: 15,
  save_transcripts: true,
  voice_history_enabled: true,
  wake_word_enabled: false,
  confirm_destructive_actions: true,
};

export interface VoiceMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  input_type: "voice" | "text";
  timestamp: string;
  tool_calls?: any[];
}

export interface ScreenContext {
  page: string;
  entity_type?: string;
  entity_title?: string;
  entity_id?: string;
}

export interface VoiceChatRequest {
  transcript: string;
  conversation_id?: string;
  screen_context?: ScreenContext;
  language?: string;
  provider?: string;
  input_type: "voice";
}

export interface VoiceChatResponse {
  conversation_id: string;
  message_id: string;
  reply: string;
  provider: string;
  model: string;
  tool_calls?: any[];
  tokens_used: number;
  requires_confirmation: boolean;
  confirmation_prompt?: string;
  input_type: "voice";
}

export const VOICE_STATE_LABELS: Record<VoiceState, string> = {
  [VoiceState.IDLE]: "Ready",
  [VoiceState.LISTENING]: "Listening...",
  [VoiceState.PROCESSING]: "Thinking...",
  [VoiceState.EXECUTING]: "Working...",
  [VoiceState.SPEAKING]: "Speaking...",
};

export const VOICE_STATE_COLORS: Record<VoiceState, string> = {
  [VoiceState.IDLE]: "#6366f1",
  [VoiceState.LISTENING]: "#10b981",
  [VoiceState.PROCESSING]: "#f59e0b",
  [VoiceState.EXECUTING]: "#06b6d4",
  [VoiceState.SPEAKING]: "#8b5cf6",
};

/** Check if browser supports Web Speech API */
export const isSpeechRecognitionSupported = (): boolean => {
  if (typeof window === "undefined") return false;
  return "SpeechRecognition" in window || "webkitSpeechRecognition" in window;
};

export const isSpeechSynthesisSupported = (): boolean => {
  if (typeof window === "undefined") return false;
  return "speechSynthesis" in window;
};

/** Get available browser TTS voices */
export const getAvailableVoices = (): SpeechSynthesisVoice[] => {
  if (!isSpeechSynthesisSupported()) return [];
  return window.speechSynthesis.getVoices();
};
