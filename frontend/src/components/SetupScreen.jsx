import { useState } from "react";
import { connectShopify, checkHealth } from "../utils/api";

const DEMO_QUERIES = [
  "White sneakers under ₹1500",
  "Gift for mom under ₹600",
  "Wireless earbuds with bass",
  "Office outfit for men",
  "Home decor under ₹800",
  "Yoga mat for beginners",
];

const HOW_IT_WORKS = [
  { icon: "✍️", title: "Type naturally", desc: "Ask in plain English — no filters needed" },
  { icon: "🧠", title: "AI parses intent", desc: "Claude extracts budget, category & preferences" },
  { icon: "🏆", title: "Ranked picks", desc: "FAISS + LLM ranks products with explanations" },
];

export default function SetupScreen({ onLaunch }) {
  const [shopUrl,    setShopUrl]    = useState("");
  const [shopToken,  setShopToken]  = useState("");
  const [status,     setStatus]     = useState(null);
  const [connecting, setConnecting] = useState(false);

  async function handleLaunch() {
    try { await checkHealth(); }
    catch {
      setStatus({ type: "error", text: "Backend not reachable. Make sure FastAPI is running on port 8000." });
      return;
    }

    if (shopUrl && shopToken) {
      setConnecting(true);
      setStatus({ type: "loading", text: "Connecting to Shopify and building search index…" });
      try {
        const res = await connectShopify(shopUrl.trim(), shopToken.trim());
        setStatus({ type: "success", text: res.message });
        setTimeout(() => onLaunch({ shopify: true, productCount: res.products_cached }), 900);
      } catch (err) {
        const msg = err.response?.data?.detail || err.message || "Shopify connection failed.";
        setStatus({ type: "error", text: `${msg} — Launching with demo data instead.` });
        setTimeout(() => onLaunch({ shopify: false, productCount: 10 }), 2000);
      } finally { setConnecting(false); }
    } else {
      onLaunch({ shopify: false, productCount: 10 });
    }
  }

  const dotColor = { loading: "bg-yellow-400 animate-pulse-soft", success: "bg-accent2", error: "bg-accent3" }[status?.type] || "";

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6 overflow-hidden"
      style={{ background: "radial-gradient(ellipse 90% 60% at 50% -5%, rgba(124,111,255,0.18), transparent), radial-gradient(ellipse 60% 40% at 80% 80%, rgba(0,223,168,0.08), transparent), #08080f" }}
    >
      <div className="w-full max-w-[900px] grid md:grid-cols-2 gap-0 bg-surface border border-border rounded-3xl overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.7)] animate-fade-up">

        {/* ── Left panel: brand + how it works ── */}
        <div className="p-10 flex flex-col gap-7 border-r border-border bg-[rgba(16,16,24,0.6)]">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl gradient-bg flex items-center justify-center text-2xl shadow-[0_4px_16px_rgba(124,111,255,0.4)]">🛍️</div>
            <div>
              <div className="font-syne font-extrabold text-2xl gradient-text">Pixelcart</div>
              <div className="text-muted text-xs mt-0.5">AI Shopping Agent · Track 01</div>
            </div>
          </div>

          {/* Tagline */}
          <p className="text-muted text-[14px] leading-relaxed border-l-2 border-accent pl-3">
            Replace <span className="text-[#ececf5]">browse → filter → search</span> with a single natural language conversation.
          </p>

          {/* How it works */}
          <div className="flex flex-col gap-3">
            <p className="text-[10px] uppercase tracking-widest text-muted2">How it works</p>
            {HOW_IT_WORKS.map((s, i) => (
              <div key={s.title} className="flex items-start gap-3 animate-fade-up" style={{ animationDelay: `${0.1 + i * 0.08}s` }}>
                <div className="w-8 h-8 rounded-xl bg-s3 border border-border flex items-center justify-center text-base flex-shrink-0">{s.icon}</div>
                <div>
                  <div className="text-[#ececf5] text-[13px] font-semibold font-syne">{s.title}</div>
                  <div className="text-muted text-[12px] mt-0.5">{s.desc}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Demo query chips */}
          <div className="flex flex-col gap-2">
            <p className="text-[10px] uppercase tracking-widest text-muted2">Try asking…</p>
            <div className="flex flex-wrap gap-1.5">
              {DEMO_QUERIES.map((q) => (
                <span
                  key={q}
                  className="text-[11px] bg-s2 border border-border text-muted px-2.5 py-1 rounded-full hover:border-accent hover:text-accent transition-all cursor-default"
                >
                  {q}
                </span>
              ))}
            </div>
          </div>

          {/* Stack badges */}
          <div className="flex gap-2 flex-wrap mt-auto">
            {["Claude AI", "FAISS", "Shopify", "FastAPI", "React"].map((t) => (
              <span key={t} className="text-[10px] bg-s3 border border-border text-muted2 px-2 py-0.5 rounded-full">{t}</span>
            ))}
          </div>
        </div>

        {/* ── Right panel: connection form ── */}
        <div className="p-10 flex flex-col gap-5">
          <div>
            <h1 className="font-syne font-extrabold text-xl text-[#ececf5]">Get started</h1>
            <p className="text-muted text-[13px] mt-1">Connect your Shopify store or jump in with demo products.</p>
          </div>

          {/* Backend notice */}
          <div className="bg-[rgba(124,111,255,0.08)] border border-[rgba(124,111,255,0.2)] rounded-xl px-4 py-3 text-[11.5px] text-muted leading-relaxed">
            ⚡ Make sure the <span className="text-accent font-medium">FastAPI backend</span> is running on <span className="text-[#ececf5]">localhost:8000</span><br/>
            <span className="text-muted2 font-mono text-[10.5px]">uvicorn main:app --reload</span>
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3 text-muted2 text-[10px] uppercase tracking-wider">
            <div className="flex-1 h-px bg-border" />
            Shopify (optional)
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Store URL */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] text-muted uppercase tracking-wider">Store URL</label>
            <input
              className="input-field"
              type="text"
              placeholder="your-store.myshopify.com"
              value={shopUrl}
              onChange={(e) => setShopUrl(e.target.value)}
              autoComplete="off"
              id="shopify-url"
            />
          </div>

          {/* Token */}
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] text-muted uppercase tracking-wider">Storefront Access Token</label>
            <input
              className="input-field"
              type="password"
              placeholder="Storefront API token…"
              value={shopToken}
              onChange={(e) => setShopToken(e.target.value)}
              autoComplete="off"
              id="shopify-token"
            />
            <p className="text-[10px] text-muted2 leading-relaxed">
              Shopify Admin → Settings → Apps → Develop apps → Create app → Storefront API → read_products → Install → copy token.
            </p>
          </div>

          {/* Status */}
          {status && (
            <div className="flex items-center gap-2.5 bg-s2 border border-border rounded-xl px-4 py-3 text-[12px] text-muted animate-fade-up">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />
              <span>{status.text}</span>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 mt-auto">
            <button
              id="launch-btn"
              className="btn-primary flex-1"
              onClick={handleLaunch}
              disabled={connecting}
            >
              {connecting ? "Connecting…" : "Launch Pixelcart →"}
            </button>
            <button
              id="demo-btn"
              className="btn-ghost"
              onClick={() => onLaunch({ shopify: false, productCount: 10 })}
            >
              Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
