"use client";

import { useEffect, useRef, useState } from "react";
import {
  Bot,
  CheckCircle2,
  ChevronRight,
  Clock,
  CornerDownLeft,
  Maximize2,
  Minimize2,
  RefreshCw,
  Send,
  Sparkles,
  Trash2,
  User,
  Wrench,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { ToolCallItem } from "@/lib/types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls?: ToolCallItem[];
  provider?: string;
  timestamp: string;
}

interface AIDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  initialPrompt?: string;
}

export default function AIDrawer({ isOpen, onClose, initialPrompt }: AIDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello Alex! I am your **Personalix OS Assistant**.\n\nI have access to your tasks, goals, projects, habits, calendar, and knowledge base. How can I assist you today?",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [isExpanded, setIsExpanded] = useState(false);
  const [provider, setProvider] = useState("auto");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
    }
  }, [initialPrompt]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  if (!isOpen) return null;

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: "Just now",
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await api.sendChatMessage(text, conversationId, provider);
      setConversationId(resp.conversation_id);

      const assistantMsg: Message = {
        id: resp.message_id,
        role: "assistant",
        content: resp.reply,
        tool_calls: resp.tool_calls,
        provider: resp.provider,
        timestamp: "Just now",
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Error: ${err.message || "Failed to reach AI provider"}`,
        timestamp: "Just now",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    "Plan my day",
    "What should I focus on today?",
    "Prepare my weekly review",
    "Find backend architecture notes",
    "Add high priority task: Deploy staging cluster",
  ];

  return (
    <div
      className={`fixed inset-y-0 right-0 z-50 bg-[#0d121f]/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl flex flex-col transition-all duration-300 ${
        isExpanded ? "w-full md:w-3/4" : "w-full md:w-[480px]"
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#111726]/60">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              Personalix Assistant
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Agent Active
              </span>
            </h2>
            <p className="text-[10px] text-slate-400">Context-Aware AI Command Center</p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {/* Provider selector */}
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-300 text-[10px] rounded px-2 py-1 outline-none"
          >
            <option value="auto">Auto Provider</option>
            <option value="openai">OpenAI GPT-4o</option>
            <option value="anthropic">Claude 3.5 Sonnet</option>
            <option value="gemini">Google Gemini</option>
            <option value="fallback">Offline Heuristic</option>
          </select>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-800 transition-colors"
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 text-xs leading-relaxed ${
              msg.role === "user" ? "flex-row-reverse" : "flex-row"
            }`}
          >
            <div
              className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-gradient-to-tr from-purple-600 to-indigo-600 text-white"
              }`}
            >
              {msg.role === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            <div
              className={`max-w-[85%] rounded-2xl p-3.5 space-y-2 ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md"
                  : "bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none shadow-sm"
              }`}
            >
              <div className="whitespace-pre-wrap font-sans">{msg.content}</div>

              {/* Tool Execution Badges */}
              {msg.tool_calls && msg.tool_calls.length > 0 && (
                <div className="pt-2 mt-2 border-t border-slate-800/80 space-y-1.5">
                  <span className="text-[10px] uppercase font-bold text-slate-400 flex items-center gap-1">
                    <Wrench className="w-3 h-3 text-indigo-400" /> Actions Dispatched:
                  </span>
                  {msg.tool_calls.map((tc, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded bg-slate-950/80 border border-indigo-500/20 text-[11px] font-mono text-indigo-300 flex items-center justify-between"
                    >
                      <span>⚡ {tc.name}</span>
                      <span className="text-emerald-400 text-[10px] flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> {tc.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 text-xs">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center animate-pulse">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl rounded-tl-none p-3 text-slate-400 flex items-center gap-2">
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-400" />
              <span>Personalix reasoning & executing tools...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Actions */}
      <div className="p-2.5 border-t border-slate-800/60 bg-[#111726]/40 overflow-x-auto whitespace-nowrap">
        <div className="flex items-center gap-1.5">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              className="px-2.5 py-1 rounded-full bg-slate-800 hover:bg-indigo-600/20 text-slate-400 hover:text-indigo-300 border border-slate-700/60 text-[11px] transition-all shrink-0"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-slate-800 bg-[#0d121f]">
        <div className="flex items-center gap-2 p-2 rounded-xl bg-slate-900 border border-slate-700/80 focus-within:border-indigo-500 transition-colors">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask AI to plan, manage tasks, search knowledge..."
            className="w-full bg-transparent border-none outline-none text-xs text-white placeholder-slate-500 px-1"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
            className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white transition-all shadow-sm"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
