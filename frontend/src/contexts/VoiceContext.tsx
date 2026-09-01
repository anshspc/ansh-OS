"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { usePathname } from "next/navigation";
import {
  DEFAULT_VOICE_SETTINGS,
  isSpeechRecognitionSupported,
  isSpeechSynthesisSupported,
  ScreenContext,
  VoiceChatResponse,
  VoiceMessage,
  VoiceSettings,
  VoiceState,
} from "@/lib/voice";
import { api } from "@/lib/api";

// ─── API call ────────────────────────────────────────────────────────────────

async function sendVoiceChat(
  transcript: string,
  conversationId: string | undefined,
  screenContext: ScreenContext,
  language: string,
  settings: VoiceSettings
): Promise<VoiceChatResponse> {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("personalix_token")
      : null;

  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/voice/chat`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        transcript,
        conversation_id: conversationId,
        screen_context: screenContext,
        language,
        input_type: "voice",
      }),
    }
  );
  if (!res.ok) throw new Error(`Voice API error ${res.status}`);
  return res.json();
}

// ─── Context shape ────────────────────────────────────────────────────────────

interface VoiceContextValue {
  voiceState: VoiceState;
  isSupported: boolean;
  isActive: boolean;           // overlay is open
  transcript: string;          // live STT transcript
  lastResponse: string;        // most recent AI reply
  messages: VoiceMessage[];
  conversationId: string | undefined;
  settings: VoiceSettings;
  pendingConfirmation: { prompt: string } | null;

  openVoice: () => void;
  closeVoice: () => void;
  toggleVoice: () => void;
  startListening: () => void;
  stopListening: () => void;
  speak: (text: string) => void;
  stopSpeaking: () => void;
  confirmAction: (confirmed: boolean) => void;
  updateSettings: (s: Partial<VoiceSettings>) => void;
}

const VoiceContext = createContext<VoiceContextValue | null>(null);

// ─── Provider ────────────────────────────────────────────────────────────────

export function VoiceProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const [voiceState, setVoiceState] = useState<VoiceState>(VoiceState.IDLE);
  const [isActive, setIsActive] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interimTranscript, setInterimTranscript] = useState("");
  const [lastResponse, setLastResponse] = useState("");
  const [messages, setMessages] = useState<VoiceMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [settings, setSettings] = useState<VoiceSettings>(DEFAULT_VOICE_SETTINGS);
  const [pendingConfirmation, setPendingConfirmation] = useState<{
    prompt: string;
    originalTranscript: string;
  } | null>(null);

  const recognitionRef = useRef<any>(null);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const isSupported =
    isSpeechRecognitionSupported() && isSpeechSynthesisSupported();

  // Build screen context from current URL
  const buildScreenContext = useCallback((): ScreenContext => {
    const segments = pathname?.split("/").filter(Boolean) || [];
    return {
      page: segments[0] || "dashboard",
      entity_type: segments[1] ? segments[0] : undefined,
      entity_title: segments[1] || undefined,
      entity_id: segments[2] || undefined,
    };
  }, [pathname]);

  // ── TTS ──────────────────────────────────────────────────────────────────

  const stopSpeaking = useCallback(() => {
    if (isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel();
    }
    setVoiceState(VoiceState.IDLE);
  }, []);

  const speak = useCallback(
    (text: string) => {
      if (!isSpeechSynthesisSupported() || !text.trim()) return;
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = settings.voice_speed;
      utterance.pitch = settings.voice_pitch;
      utterance.lang = settings.language;

      if (settings.voice_name) {
        const voices = window.speechSynthesis.getVoices();
        const match = voices.find((v) => v.name === settings.voice_name);
        if (match) utterance.voice = match;
      }

      utterance.onstart = () => setVoiceState(VoiceState.SPEAKING);
      utterance.onend = () => setVoiceState(VoiceState.IDLE);
      utterance.onerror = () => setVoiceState(VoiceState.IDLE);

      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
      setVoiceState(VoiceState.SPEAKING);
    },
    [settings]
  );

  // ── STT ──────────────────────────────────────────────────────────────────

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setVoiceState(VoiceState.IDLE);
  }, []);

  const processTranscript = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      setTranscript(text);
      setVoiceState(VoiceState.PROCESSING);

      const userMsg: VoiceMessage = {
        id: Date.now().toString(),
        role: "user",
        content: text,
        input_type: "voice",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const screenCtx = buildScreenContext();
        const resp = await sendVoiceChat(
          text,
          conversationId,
          screenCtx,
          settings.language,
          settings
        );

        setConversationId(resp.conversation_id);

        if (resp.requires_confirmation) {
          setPendingConfirmation({
            prompt: resp.reply,
            originalTranscript: text,
          });
          setLastResponse(resp.reply);
          if (settings.auto_speak) speak(resp.reply);
          setVoiceState(VoiceState.IDLE);
          return;
        }

        setVoiceState(VoiceState.EXECUTING);
        setLastResponse(resp.reply);

        const assistantMsg: VoiceMessage = {
          id: resp.message_id || Date.now().toString() + "_ai",
          role: "assistant",
          content: resp.reply,
          input_type: "voice",
          timestamp: new Date().toISOString(),
          tool_calls: resp.tool_calls,
        };
        setMessages((prev) => [...prev, assistantMsg]);

        if (settings.auto_speak) {
          speak(resp.reply);
        } else {
          setVoiceState(VoiceState.IDLE);
        }
      } catch (err: any) {
        const errText = "Sorry, I couldn't process that. Please try again.";
        setLastResponse(errText);
        if (settings.auto_speak) speak(errText);
        else setVoiceState(VoiceState.IDLE);
      }
    },
    [conversationId, settings, buildScreenContext, speak]
  );

  const startListening = useCallback(() => {
    if (!isSpeechRecognitionSupported()) return;
    // Stop TTS if speaking
    stopSpeaking();

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = settings.language;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setVoiceState(VoiceState.LISTENING);
      setInterimTranscript("");
    };

    recognition.onresult = (event: any) => {
      let interim = "";
      let final = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          final += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }
      setInterimTranscript(interim);
      if (final) {
        setInterimTranscript("");
        processTranscript(final.trim());
      }
    };

    recognition.onerror = (event: any) => {
      console.warn("Voice recognition error:", event.error);
      setVoiceState(VoiceState.IDLE);
    };

    recognition.onend = () => {
      if (voiceState === VoiceState.LISTENING) {
        setVoiceState(VoiceState.IDLE);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [settings.language, stopSpeaking, processTranscript, voiceState]);

  // ── Confirmation ─────────────────────────────────────────────────────────

  const confirmAction = useCallback(
    (confirmed: boolean) => {
      if (!pendingConfirmation) return;
      if (confirmed) {
        // Re-send with "yes, confirmed" prefix so AI knows to execute
        processTranscript("Yes, confirmed. " + pendingConfirmation.originalTranscript);
      } else {
        const cancelMsg = "Understood. Action cancelled.";
        setLastResponse(cancelMsg);
        if (settings.auto_speak) speak(cancelMsg);
      }
      setPendingConfirmation(null);
    },
    [pendingConfirmation, processTranscript, settings.auto_speak, speak]
  );

  // ── Overlay controls ──────────────────────────────────────────────────────

  const openVoice = useCallback(() => setIsActive(true), []);
  const closeVoice = useCallback(() => {
    stopListening();
    stopSpeaking();
    setIsActive(false);
    setVoiceState(VoiceState.IDLE);
  }, [stopListening, stopSpeaking]);

  const toggleVoice = useCallback(() => {
    if (isActive) closeVoice();
    else openVoice();
  }, [isActive, openVoice, closeVoice]);

  // ── Global Ctrl+Space hotkey ──────────────────────────────────────────────

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.code === "Space") {
        e.preventDefault();
        if (!isActive) {
          openVoice();
        } else if (voiceState === VoiceState.LISTENING) {
          stopListening();
        } else if (voiceState === VoiceState.SPEAKING) {
          stopSpeaking();
        } else {
          startListening();
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [isActive, voiceState, openVoice, stopListening, stopSpeaking, startListening]);

  const updateSettings = useCallback((s: Partial<VoiceSettings>) => {
    setSettings((prev) => ({ ...prev, ...s }));
  }, []);

  return (
    <VoiceContext.Provider
      value={{
        voiceState,
        isSupported,
        isActive,
        transcript,
        lastResponse,
        messages,
        conversationId,
        settings,
        pendingConfirmation: pendingConfirmation
          ? { prompt: pendingConfirmation.prompt }
          : null,
        openVoice,
        closeVoice,
        toggleVoice,
        startListening,
        stopListening,
        speak,
        stopSpeaking,
        confirmAction,
        updateSettings,
      }}
    >
      {children}
    </VoiceContext.Provider>
  );
}

export function useVoice(): VoiceContextValue {
  const ctx = useContext(VoiceContext);
  if (!ctx) throw new Error("useVoice must be used inside <VoiceProvider>");
  return ctx;
}
