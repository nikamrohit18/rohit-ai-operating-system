"use client";

import { useState, useRef, useEffect } from "react";
import { askDigitalTwin, pollTask, getVoiceUrl } from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  taskId?: string;
  loading?: boolean;
}

const SUGGESTIONS = [
  "What is Rohit working on right now?",
  "What are his AI consulting services?",
  "What tech stack does he use?",
  "How can I collaborate with Rohit?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef<string>(crypto.randomUUID());

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send(question: string) {
    if (!question.trim() || sending) return;
    setSending(true);
    setInput("");

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text: question };
    const loadingMsg: Message = { id: crypto.randomUUID(), role: "assistant", text: "", loading: true };
    setMessages((prev) => [...prev, userMsg, loadingMsg]);

    try {
      const { task_id } = await askDigitalTwin(question, sessionId.current);

      // Poll until completed
      let result = await pollTask(task_id);
      while (result.status === "pending" || result.status === "running") {
        await new Promise((r) => setTimeout(r, 2000));
        result = await pollTask(task_id);
      }

      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMsg.id
            ? { ...m, text: result.output || "Sorry, I couldn't process that.", loading: false, taskId: task_id }
            : m
        )
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === loadingMsg.id
            ? { ...m, text: "Something went wrong. Is the API server running?", loading: false }
            : m
        )
      );
    } finally {
      setSending(false);
    }
  }

  async function playVoice(taskId: string) {
    try {
      const res = await fetch(getVoiceUrl(taskId));
      if (!res.ok) {
        alert("Voice is not configured yet. Add ELEVENLABS_API_KEY to your .env file to enable it.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    } catch {
      alert("Could not play voice. Make sure the API server is running.");
    }
  }

  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4 flex items-center gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold text-sm">
          RN
        </div>
        <div>
          <h1 className="font-semibold text-white text-sm">Rohit Nikam</h1>
          <p className="text-xs text-slate-400">AI Systems Builder · Digital Twin</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-slate-400">Online</span>
        </div>
      </header>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full min-h-[60vh] gap-8">
            <div className="text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4">
                RN
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">Talk to Rohit&apos;s Digital Twin</h2>
              <p className="text-slate-400 text-sm max-w-md">
                Ask me anything about Rohit&apos;s work, AI projects, consulting services, or how to collaborate.
              </p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left px-4 py-3 rounded-xl border border-slate-700 text-slate-300 text-sm hover:border-violet-500 hover:text-white transition-all bg-slate-900/50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-semibold ${
                  msg.role === "user"
                    ? "bg-slate-700 text-slate-300"
                    : "bg-gradient-to-br from-violet-500 to-cyan-500 text-white"
                }`}
              >
                {msg.role === "user" ? "You" : "RN"}
              </div>
              <div className={`max-w-[80%] ${msg.role === "user" ? "items-end" : "items-start"} flex flex-col gap-1`}>
                <div
                  className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-violet-600 text-white rounded-tr-sm"
                      : "bg-slate-800 text-slate-200 rounded-tl-sm"
                  }`}
                >
                  {msg.loading ? (
                    <div className="flex gap-1 items-center h-4">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]" />
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]" />
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]" />
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  )}
                </div>
                {msg.taskId && !msg.loading && (
                  <button
                    onClick={() => playVoice(msg.taskId!)}
                    className="text-xs text-slate-500 hover:text-violet-400 transition-colors flex items-center gap-1 px-1"
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                    </svg>
                    Play voice
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-800 px-4 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask Rohit anything..."
            disabled={sending}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 outline-none focus:border-violet-500 transition-colors disabled:opacity-50"
          />
          <button
            onClick={() => send(input)}
            disabled={sending || !input.trim()}
            className="px-5 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
          >
            {sending ? "..." : "Send"}
          </button>
        </div>
      </div>
    </main>
  );
}
