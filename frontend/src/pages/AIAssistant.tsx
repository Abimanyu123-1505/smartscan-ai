import { useState, useRef, useEffect } from "react";
import { useParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Send, User, Loader } from "lucide-react";
import PageWrapper from "../components/shared/PageWrapper";
import { aiApi } from "../api/client";
import type { AIMessage } from "../types";

export default function AIAssistant() {
  const { caseId } = useParams<{ caseId: string }>();
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: AIMessage = { role: "user", content: input, citations: [], ts: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await aiApi.chat(caseId!, input, sessionId);
      if (!sessionId) setSessionId(res.session_id);
      const aiMsg: AIMessage = {
        role: "assistant",
        content: res.content,
        citations: (res.citations as unknown as AIMessage["citations"]) ?? [],
        ts: res.timestamp,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errMsg: AIMessage = { role: "assistant", content: "Error: Could not reach AI backend.", citations: [], ts: new Date().toISOString() };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper title="AI Investigation Assistant" subtitle="Case-aware forensic assistant powered by RAG over your evidence">
      <div className="flex flex-col" style={{ height: "calc(100vh - 220px)" }}>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#bc8cff] to-[#388bfd] flex items-center justify-center mb-4 opacity-80">
                <Bot size={28} className="text-white" />
              </div>
              <h2 className="text-lg font-semibold text-[#e6edf3] mb-2">AI Forensic Assistant</h2>
              <p className="text-sm text-[#8b949e] max-w-sm">
                Ask questions about your case evidence, artifacts, IOCs, or request analysis summaries.
              </p>
              <div className="mt-6 grid grid-cols-2 gap-3 text-left max-w-lg">
                {[
                  "Summarize all suspicious processes found in memory",
                  "What registry run keys were added recently?",
                  "List all external IP connections and flag suspicious ones",
                  "Generate a timeline of attacker activity",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setInput(suggestion)}
                    className="text-xs text-left p-3 bg-[#161b22] border border-[#21262d] rounded-xl text-[#8b949e] hover:border-[#388bfd] hover:text-[#e6edf3] transition-all"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    msg.role === "user"
                      ? "bg-gradient-to-br from-[#388bfd] to-[#1f6feb]"
                      : "bg-gradient-to-br from-[#bc8cff] to-[#388bfd]"
                  }`}
                >
                  {msg.role === "user" ? <User size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
                </div>
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user"
                      ? "bg-[#388bfd] text-white rounded-tr-md"
                      : "bg-[#161b22] border border-[#21262d] text-[#e6edf3] rounded-tl-md"
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                  {msg.citations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-[rgba(255,255,255,0.1)] space-y-1">
                      {msg.citations.map((c, j) => (
                        <div key={j} className="text-[10px] font-mono opacity-70">→ {c.label || c.ref}</div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#bc8cff] to-[#388bfd] flex items-center justify-center">
                <Bot size={14} className="text-white" />
              </div>
              <div className="bg-[#161b22] border border-[#21262d] rounded-2xl rounded-tl-md px-4 py-3 flex items-center gap-2">
                <Loader size={14} className="animate-spin text-[#bc8cff]" />
                <span className="text-xs text-[#484f58]">Analyzing evidence...</span>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex gap-3 items-end">
          <div className="flex-1 bg-[#161b22] border border-[#30363d] rounded-xl px-4 py-3 focus-within:border-[#388bfd] transition-colors">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Ask about evidence, artifacts, or request analysis..."
              rows={2}
              className="w-full bg-transparent text-[#e6edf3] text-sm outline-none resize-none placeholder:text-[#484f58]"
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="w-10 h-10 rounded-xl bg-[#388bfd] flex items-center justify-center text-white hover:bg-[#1f6feb] disabled:opacity-40 transition-all shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
        <div className="text-[10px] text-[#484f58] text-center mt-2">Press Enter to send · Shift+Enter for new line</div>
      </div>
    </PageWrapper>
  );
}
