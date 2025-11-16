"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import api from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Send, User } from "lucide-react";

type Msg = { role: "user" | "assistant"; text: string; id: string };

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", text: "Hi! I can track expenses and parse receipts.", id: crypto.randomUUID() },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const viewportRef = useRef<HTMLDivElement>(null);

  const sessionId = useMemo(() => {
    if (typeof window === "undefined") return "default";
    return localStorage.getItem("session_id") ?? (() => {
      const sid = `s_${Date.now().toString(36)}`;
      localStorage.setItem("session_id", sid);
      return sid;
    })();
  }, []);

  useEffect(() => {
    // scroll to bottom smoothly whenever messages update
    const el = viewportRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  async function send() {
    const msg = input.trim();
    if (!msg || thinking) return;
    const userMsg: Msg = { role: "user", text: msg, id: crypto.randomUUID() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setThinking(true);
    try {
      const { data } = await api.post("/api/chat", { message: msg, session_id: sessionId });
      const botMsg: Msg = { role: "assistant", text: data.text ?? "", id: crypto.randomUUID() };
      setMessages((m) => [...m, botMsg]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "Error contacting backend.", id: crypto.randomUUID() }]);
    } finally {
      setThinking(false);
    }
  }

  return (
    <div className="w-full max-w-5xl mx-auto px-4">
      <div className="rounded-2xl border bg-white/70 backdrop-blur p-4 shadow-sm">
        <div
          ref={viewportRef}
          className="h-[380px] overflow-y-auto pr-1 scroll-smooth"
        >
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`mb-3 flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex items-start gap-2 max-w-[78%]`}>
                  {m.role === "assistant" && (
                    <div className="h-8 w-8 rounded-full bg-black text-white grid place-items-center shrink-0">
                      <Bot size={16} />
                    </div>
                  )}
                  <div
                    className={`px-3 py-2 rounded-2xl shadow-sm ${
                      m.role === "user"
                        ? "bg-black text-white"
                        : "bg-zinc-100 text-zinc-900"
                    }`}
                  >
                    {m.text}
                  </div>
                  {m.role === "user" && (
                    <div className="h-8 w-8 rounded-full bg-zinc-200 grid place-items-center shrink-0">
                      <User size={16} />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {thinking && (
            <div className="flex items-center gap-2 text-zinc-600 text-sm">
              <div className="h-8 w-8 rounded-full bg-black text-white grid place-items-center shrink-0">
                <Bot size={16} />
              </div>
              <span className="animate-pulse">Thinking…</span>
            </div>
          )}
        </div>

        <div className="mt-3 flex gap-2">
          <input
            className="flex-1 border rounded-xl px-3 py-2 bg-white"
            placeholder="Ask me to add an expense or for a summary…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button
            onClick={send}
            disabled={!input.trim() || thinking}
            className="px-4 py-2 rounded-xl bg-black text-white disabled:opacity-50 flex items-center gap-2"
            title="Send"
          >
            <Send size={16} />
            Send
          </button>
        </div>
        <p className="text-xs text-zinc-500 mt-2">
          Tip: try <i>"Add 12.50 to Dining from Starbucks on 2025-11-01"</i>
        </p>
      </div>
    </div>
  );
}