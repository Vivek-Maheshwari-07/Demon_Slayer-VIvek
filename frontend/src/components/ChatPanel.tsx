import React, { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Sparkles } from "lucide-react";
import { CitationCard } from "./CitationCard";
import { apiClient } from "../api/client";

interface Citation {
  text: string;
  page: number;
  chunk_id: string;
}

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  citations?: Citation[];
}

interface ChatPanelProps {
  paperId: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ paperId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "bot",
      text: "Welcome! I have parsed and index-partitioned the paper. You can ask me any question about the methodology, results, or limitations, and I will answer with verified page citations.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput("");
    
    // Add user message
    const userMessage: Message = {
      id: strUuid(),
      sender: "user",
      text: userText,
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const data = await apiClient.askQuestion(paperId, userText);
      
      const botMessage: Message = {
        id: strUuid(),
        sender: "bot",
        text: data.answer,
        citations: data.citations || [],
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        id: strUuid(),
        sender: "bot",
        text: `Error: ${err.message || "Failed to communicate with backend."}`,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Quick helpers
  const strUuid = () => Math.random().toString(36).substring(2, 9);

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] bg-slate-950/20 border border-slate-900 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
      {/* Panel Header */}
      <div className="px-6 py-4 bg-slate-950/60 border-b border-slate-900 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Bot className="w-5 h-5 text-violet-400" />
          <h2 className="text-sm font-bold text-white tracking-wide">Grounding Q&A Engine</h2>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span className="text-[10px] text-emerald-400 font-semibold tracking-wider uppercase">
            Factual Mode Active
          </span>
        </div>
      </div>

      {/* Messages List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((msg) => {
          const isBot = msg.sender === "bot";
          return (
            <div
              key={msg.id}
              className={`flex gap-4 max-w-[85%] ${
                isBot ? "mr-auto" : "ml-auto flex-row-reverse"
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-xl shrink-0 flex items-center justify-center border shadow-md ${
                  isBot
                    ? "bg-slate-900 border-slate-800 text-violet-400"
                    : "bg-violet-600 border-violet-500 text-white"
                }`}
              >
                {isBot ? <Bot className="w-4.5 h-4.5" /> : <User className="w-4.5 h-4.5" />}
              </div>

              {/* Message Content */}
              <div className="space-y-2">
                <div
                  className={`p-4 rounded-2xl text-[14px] leading-relaxed shadow-sm border ${
                    isBot
                      ? "bg-slate-900/60 border-slate-900 text-slate-200 rounded-tl-none"
                      : "bg-violet-600/15 border-violet-500/20 text-slate-100 rounded-tr-none"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                </div>

                {/* Citations List */}
                {isBot && msg.citations && msg.citations.length > 0 && (
                  <div className="flex flex-col items-start gap-1 mt-1 pl-1">
                    <div className="flex items-center gap-1 text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">
                      <Sparkles className="w-3 h-3 text-violet-400" />
                      <span>Factual Attributions:</span>
                    </div>
                    <div className="flex flex-wrap gap-2 w-full">
                      {msg.citations.map((cit, cidx) => (
                        <CitationCard
                          key={cit.chunk_id || cidx}
                          text={cit.text}
                          page={cit.page}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-4 max-w-[80%] mr-auto">
            <div className="w-9 h-9 rounded-xl shrink-0 flex items-center justify-center bg-slate-900 border border-slate-800 text-violet-400 animate-pulse">
              <Bot className="w-4.5 h-4.5" />
            </div>
            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-2 p-4 bg-slate-900/40 border border-slate-900 rounded-2xl rounded-tl-none">
                <Loader2 className="w-4 h-4 text-violet-500 animate-spin" />
                <span className="text-xs text-slate-400">Consulting document index...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={handleSend}
        className="p-4 bg-slate-950/60 border-t border-slate-900 flex gap-3"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the methodology, results, or equations..."
          className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500/80 focus:ring-1 focus:ring-violet-500/40 transition-all duration-200"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-3 bg-violet-600 hover:bg-violet-500 disabled:bg-slate-900 text-white disabled:text-slate-600 rounded-xl transition-all duration-200 shadow-lg shadow-violet-500/10 cursor-pointer disabled:cursor-not-allowed shrink-0"
        >
          <Send className="w-4.5 h-4.5" />
        </button>
      </form>
    </div>
  );
};
