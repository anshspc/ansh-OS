"use client";

import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import Header from "@/components/Header";
import CommandPalette from "@/components/CommandPalette";
import AIDrawer from "@/components/ai/AIDrawer";
import { VoiceProvider } from "@/contexts/VoiceContext";
import VoiceOverlay from "@/components/voice/VoiceOverlay";
import VoiceButton from "@/components/voice/VoiceButton";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [isAIOpen, setIsAIOpen] = useState(false);
  const [aiInitialPrompt, setAiInitialPrompt] = useState<string | undefined>();

  const handleOpenAIWithPrompt = (prompt?: string) => {
    setAiInitialPrompt(prompt);
    setIsAIOpen(true);
  };

  return (
    <VoiceProvider>
      <div className="flex min-h-screen bg-[#090d16] text-slate-100">
        {/* Collapsible Sidebar */}
        <Sidebar
          onOpenAI={() => setIsAIOpen(true)}
          onOpenCommand={() => setIsCommandOpen(true)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <Header
            onOpenCommand={() => setIsCommandOpen(true)}
            onOpenAI={() => setIsAIOpen(true)}
          />
          <main className="flex-1 p-6 overflow-y-auto max-w-7xl w-full mx-auto">
            {children}
          </main>
        </div>

        {/* Modals & Drawers */}
        <CommandPalette
          isOpen={isCommandOpen}
          onClose={() => setIsCommandOpen(false)}
          onOpenAI={handleOpenAIWithPrompt}
        />
        <AIDrawer
          isOpen={isAIOpen}
          onClose={() => setIsAIOpen(false)}
          initialPrompt={aiInitialPrompt}
        />

        {/* ── Personalix Voice ──────────────────────── */}
        {/* Floating voice button — bottom right of screen */}
        <div className="fixed bottom-6 right-6 z-50">
          <VoiceButton />
        </div>

        {/* Full-screen voice overlay */}
        <VoiceOverlay />
      </div>
    </VoiceProvider>
  );
}
