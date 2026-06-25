import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Braces, Wand2, Loader2, Tag, Gauge, Smile, User, ChevronDown } from "lucide-react";

type Ticket = {
  category: string;
  urgency: string;
  sentiment: string;
  summary: string;
  entities: string[];
  requires_human: boolean;
};
type Resp = { ok: boolean; mode?: string; attempts?: number; ticket?: Ticket; error?: string };

const URG: Record<string, string> = {
  low: "text-slate-300 bg-slate-500/15 ring-slate-500/30",
  medium: "text-sky-300 bg-sky-500/15 ring-sky-500/30",
  high: "text-amber-300 bg-amber-500/15 ring-amber-500/30",
  critical: "text-rose-300 bg-rose-500/15 ring-rose-500/30",
};
const SENT: Record<string, string> = {
  positive: "text-emerald-300 bg-emerald-500/15 ring-emerald-500/30",
  neutral: "text-slate-300 bg-slate-500/15 ring-slate-500/30",
  negative: "text-rose-300 bg-rose-500/15 ring-rose-500/30",
};

const EXAMPLES = [
  "URGENT: I was charged twice for order #4471 and I'm furious. Refund me now!",
  "Hi, just wondering how I can change my account password? No rush, thanks!",
  "The app keeps crashing every time I open the dashboard. Please fix this bug.",
];

function Blobs() {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden">
      <div className="absolute -top-44 -left-40 h-[34rem] w-[34rem] rounded-full bg-indigo-600/20 blur-3xl animate-float" />
      <div className="absolute bottom-0 -right-40 h-[30rem] w-[30rem] rounded-full bg-fuchsia-500/15 blur-3xl animate-float [animation-delay:-6s]" />
    </div>
  );
}

function Field({ icon, label, children }: { icon: any; label: string; children: React.ReactNode }) {
  const Icon = icon;
  return (
    <div className="flex items-center justify-between gap-3 border-b border-white/5 py-3">
      <span className="flex items-center gap-2 text-sm text-slate-400">
        <Icon size={15} /> {label}
      </span>
      <div className="text-right">{children}</div>
    </div>
  );
}

export default function App() {
  const [text, setText] = useState(EXAMPLES[0]);
  const [provider, setProvider] = useState("demo");
  const [apiKey, setApiKey] = useState("");
  const [resp, setResp] = useState<Resp | null>(null);
  const [loading, setLoading] = useState(false);
  const [showRaw, setShowRaw] = useState(false);

  async function run() {
    setLoading(true);
    try {
      const r = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, provider, api_key: apiKey || null }),
      });
      setResp(await r.json());
    } finally {
      setLoading(false);
    }
  }

  const t = resp?.ticket;

  return (
    <div className="relative min-h-screen text-slate-200">
      <Blobs />
      <div className="relative mx-auto max-w-3xl px-5 py-14">
        <motion.header
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-9 text-center"
        >
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs text-slate-300 backdrop-blur">
            <Braces size={14} className="text-fuchsia-300" />
            Reliable structured output · validated, never junk
          </div>
          <h1 className="text-5xl font-extrabold tracking-tight text-white sm:text-6xl">
            LLM{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-fuchsia-400 to-pink-300 bg-clip-text text-transparent">
              Extractor
            </span>
          </h1>
          <p className="mx-auto mt-4 max-w-lg text-slate-400">
            Free text in, a clean validated support ticket out. Works offline with a
            heuristic; add a provider key for real LLM extraction.
          </p>
        </motion.header>

        {/* Input */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 backdrop-blur">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a customer message…"
            className="h-28 w-full resize-none bg-transparent text-base text-white placeholder:text-slate-600 outline-none"
          />
          <div className="mt-2 flex flex-wrap items-center gap-2 border-t border-white/5 pt-3">
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-slate-200 outline-none"
            >
              <option value="demo">Demo (offline)</option>
              <option value="anthropic">Anthropic</option>
              <option value="openai">OpenAI</option>
            </select>
            {provider !== "demo" && (
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="API key"
                className="flex-1 rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-sm text-slate-200 outline-none"
              />
            )}
            <button
              onClick={run}
              disabled={loading}
              className="ml-auto inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-fuchsia-500 px-5 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
              {loading ? <Loader2 className="animate-spin" size={16} /> : <Wand2 size={16} />}
              Extract
            </button>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap justify-center gap-2">
          {EXAMPLES.map((e) => (
            <button
              key={e}
              onClick={() => setText(e)}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-400 hover:bg-white/10"
            >
              {e.length > 40 ? e.slice(0, 40) + "…" : e}
            </button>
          ))}
        </div>

        {/* Result */}
        <AnimatePresence>
          {resp && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8"
            >
              {!resp.ok ? (
                <div className="rounded-2xl border border-rose-400/20 bg-rose-400/5 p-6 text-center text-rose-300">
                  {resp.error}
                </div>
              ) : (
                t && (
                  <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur">
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
                        Extracted ticket
                      </h3>
                      <span className="rounded-full bg-white/5 px-2.5 py-0.5 text-[11px] text-slate-400">
                        {resp.mode === "llm" ? `LLM · ${resp.attempts} attempt(s)` : "heuristic demo"}
                      </span>
                    </div>

                    <Field icon={Tag} label="Category">
                      <span className="rounded-md bg-indigo-500/15 px-2.5 py-1 text-sm font-medium capitalize text-indigo-200 ring-1 ring-indigo-500/30">
                        {t.category}
                      </span>
                    </Field>
                    <Field icon={Gauge} label="Urgency">
                      <span className={`rounded-md px-2.5 py-1 text-sm font-medium capitalize ring-1 ${URG[t.urgency] ?? URG.medium}`}>
                        {t.urgency}
                      </span>
                    </Field>
                    <Field icon={Smile} label="Sentiment">
                      <span className={`rounded-md px-2.5 py-1 text-sm font-medium capitalize ring-1 ${SENT[t.sentiment] ?? SENT.neutral}`}>
                        {t.sentiment}
                      </span>
                    </Field>
                    <Field icon={User} label="Needs a human">
                      <span className={`rounded-md px-2.5 py-1 text-sm font-medium ring-1 ${t.requires_human ? "text-amber-300 bg-amber-500/15 ring-amber-500/30" : "text-emerald-300 bg-emerald-500/15 ring-emerald-500/30"}`}>
                        {t.requires_human ? "Yes" : "No"}
                      </span>
                    </Field>

                    <div className="py-3">
                      <p className="mb-1 text-sm text-slate-400">Summary</p>
                      <p className="text-slate-200">{t.summary}</p>
                    </div>
                    {t.entities.length > 0 && (
                      <div className="py-1">
                        <p className="mb-2 text-sm text-slate-400">Entities</p>
                        <div className="flex flex-wrap gap-2">
                          {t.entities.map((e, i) => (
                            <span key={i} className="rounded-full bg-white/5 px-3 py-1 font-mono text-xs text-slate-300">
                              {e}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <button
                      onClick={() => setShowRaw((s) => !s)}
                      className="mt-4 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300"
                    >
                      <ChevronDown size={14} className={showRaw ? "rotate-180 transition" : "transition"} />
                      {showRaw ? "Hide" : "Show"} raw JSON
                    </button>
                    {showRaw && (
                      <pre className="mt-2 overflow-auto rounded-xl bg-black/40 p-4 font-mono text-xs text-emerald-200">
                        {JSON.stringify(t, null, 2)}
                      </pre>
                    )}
                  </div>
                )
              )}
            </motion.div>
          )}
        </AnimatePresence>

        <footer className="mt-16 text-center text-xs text-slate-600">
          Pydantic-validated · JSON repair + retry on the LLM path · provider-agnostic
        </footer>
      </div>
    </div>
  );
}
