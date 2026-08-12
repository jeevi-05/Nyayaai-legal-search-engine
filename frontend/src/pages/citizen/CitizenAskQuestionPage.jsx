import { useState, useRef, useEffect } from "react";
import { searchCases } from "../../services/researchService";
import { Scale, Send, AlertCircle, User, Bot, FileText, Building2, Calendar } from "lucide-react";

const DISCLAIMER = "This information is for general legal awareness and not a substitute for professional legal advice.";

function buildAnswer(query, results) {
  if (!results.length) {
    return `I searched the Indian legal database for "${query}" but could not find directly matching documents. Please try rephrasing your question or consult a legal professional for guidance.`;
  }
  const top = results[0];
  let answer = `Based on the Indian legal database, here is what I found regarding "${query}":\n\n`;
  if (top.description) {
    answer += `${top.description}\n\n`;
  } else {
    answer += `The most relevant document is "${top.title}"`;
    if (top.court) answer += ` from the ${top.court}`;
    if (top.year) answer += ` (${top.year})`;
    answer += `.\n\n`;
  }
  if (results.length > 1) {
    answer += `${results.length} relevant legal documents were found. The sources below contain applicable acts, sections, and court judgments.\n\n`;
  }
  answer += `For your specific situation, please consult a qualified legal professional who can provide advice tailored to your circumstances.`;
  return answer;
}

function AiMessage({ msg }) {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-navy-100 rounded-full flex items-center justify-center shrink-0 mt-1">
        <Bot size={15} className="text-navy-600" />
      </div>
      <div className="max-w-[85%] space-y-3">
        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-gray-700 leading-relaxed shadow-sm whitespace-pre-line">
          {msg.content}
        </div>
        {msg.sources?.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide px-1">Relevant Sources</p>
            {msg.sources.map((s, i) => (
              <div key={i} className="bg-navy-50 border border-navy-100 rounded-xl px-3 py-2.5 text-xs space-y-1">
                <p className="font-semibold text-navy-700 leading-snug">{s.title}</p>
                <div className="flex flex-wrap gap-2 text-gray-500">
                  {s.court && <span className="flex items-center gap-1"><Building2 size={10} />{s.court}</span>}
                  {s.year && <span className="flex items-center gap-1"><Calendar size={10} />{s.year}</span>}
                  {s.category && <span className="flex items-center gap-1"><FileText size={10} />{s.category}</span>}
                </div>
                {s.description && <p className="text-gray-500 line-clamp-2">{s.description}</p>}
              </div>
            ))}
          </div>
        )}
        <p className="text-[10px] text-amber-600 bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5 leading-relaxed">
          ⚠️ {DISCLAIMER}
        </p>
      </div>
    </div>
  );
}

function UserMessage({ msg }) {
  return (
    <div className="flex justify-end gap-3">
      <div className="max-w-[75%] bg-emerald-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed">
        {msg.content}
      </div>
      <div className="w-8 h-8 bg-emerald-100 rounded-full flex items-center justify-center shrink-0 mt-1">
        <User size={15} className="text-emerald-600" />
      </div>
    </div>
  );
}

const INITIAL_MESSAGE = {
  role: "ai",
  content: `Hello! I am your AI legal assistant. Ask me any legal question and I will search the Indian legal database to provide relevant information, applicable laws, and court judgments.\n\nFor example:\n• "What are my rights after arrest?"\n• "How do I file a consumer complaint?"\n• "What is Article 21 of the Constitution?"`,
  sources: [],
};

export default function CitizenAskQuestionPage() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res = await searchCases(q);
      const results = res.data.results || [];
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: buildAnswer(q, results), sources: results.slice(0, 4) },
      ]);
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <div className="bg-navy-600 rounded-3xl p-7 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-white/5 pointer-events-none" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Scale size={15} className="text-navy-300" />
            <span className="text-navy-300 text-xs font-semibold uppercase tracking-widest">AI Legal Assistant</span>
          </div>
          <h1 className="text-2xl font-bold text-white">Ask Your Legal Question</h1>
          <p className="text-navy-200 text-sm mt-1">Get citizen-friendly answers backed by Indian legal documents</p>
        </div>
      </div>

      <div className="card flex flex-col" style={{ height: "540px" }}>
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {messages.map((msg, i) =>
            msg.role === "user"
              ? <UserMessage key={i} msg={msg} />
              : <AiMessage key={i} msg={msg} />
          )}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-navy-100 rounded-full flex items-center justify-center shrink-0">
                <Bot size={15} className="text-navy-600" />
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1.5 items-center h-5">
                  {[0, 150, 300].map((d) => (
                    <span key={d} className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="mx-5 mb-2 flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 rounded-xl px-3 py-2 text-xs">
            <AlertCircle size={13} className="shrink-0" /> {error}
          </div>
        )}

        <div className="border-t border-gray-100 p-4 flex gap-3">
          <textarea
            className="input-field flex-1 resize-none py-2.5 text-sm"
            rows={2}
            placeholder="Ask your legal question... (Enter to send)"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="btn-primary px-4 rounded-xl shrink-0 self-end"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
