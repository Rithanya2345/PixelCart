import { useState, useRef, useEffect } from "react";
import SetupScreen from "./components/SetupScreen";
import ChatMessage from "./components/ChatMessage";
import WelcomeBanner from "./components/WelcomeBanner";
import { useChat } from "./hooks/useChat";

const SUGGESTIONS = [
  "White sneakers under ₹1500",
  "Gift for my mom under ₹600",
  "Casual date night outfit",
  "Wireless earbuds with bass",
  "Home decor under ₹800",
  "Office wear for men",
];

const WELCOME =
  "Hey! I'm Pixelcart 🛍️ — your AI shopping assistant. Tell me what you're looking for in plain English. Try: \"white sneakers under ₹1500\" or \"a gift for my mom\".";

export default function App() {
  const [launched,  setLaunched]  = useState(false);
  const [storeInfo, setStoreInfo] = useState(null);
  const [input,     setInput]     = useState("");
  const [showSugg,  setShowSugg]  = useState(true);
  const { messages, loading, send, reset } = useChat();
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleLaunch(info) { setStoreInfo(info); setLaunched(true); }

  async function handleSend(text) {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    setShowSugg(false);
    await send(msg);
    inputRef.current?.focus();
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  }

  function handleReset() {
    reset();
    setLaunched(false);
    setStoreInfo(null);
    setShowSugg(true);
  }

  if (!launched) return <SetupScreen onLaunch={handleLaunch} />;

  return (
    <div className="flex flex-col h-screen bg-bg max-w-[920px] mx-auto w-full">

      {/* ── Header ── */}
      <header className="glass border-b border-border flex items-center justify-between px-5 py-3 flex-shrink-0 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl gradient-bg flex items-center justify-center text-base shadow-[0_2px_8px_rgba(124,111,255,0.35)]">🛍️</div>
          <span className="font-syne font-extrabold text-lg gradient-text">Pixelcart</span>
          <div className="w-px h-4 bg-border mx-1" />
          <span className="text-muted2 text-xs hidden sm:block">AI Shopping Agent</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Live connection badge */}
          <div className={`flex items-center gap-1.5 text-[11px] px-3 py-1 rounded-full border ${
            storeInfo?.shopify
              ? "bg-[rgba(0,223,168,0.07)] text-accent2 border-[rgba(0,223,168,0.2)]"
              : "bg-[rgba(120,120,160,0.07)] text-muted border-border"
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full bg-current ${storeInfo?.shopify ? "animate-pulse-soft" : ""}`} />
            {storeInfo?.shopify
              ? `Shopify · ${storeInfo.productCount} products`
              : `Demo · ${storeInfo?.productCount || 10} products`}
          </div>

          <button
            id="new-chat-btn"
            onClick={handleReset}
            className="text-[11px] text-muted border border-border rounded-lg px-3 py-1.5 hover:text-[#ececf5] hover:border-border2 transition-all"
          >
            ← New chat
          </button>
        </div>
      </header>

      {/* ── Progress bar ── */}
      {loading && (
        <div className="h-0.5 bg-border flex-shrink-0 overflow-hidden">
          <div className="h-full gradient-bg animate-pulse w-full" />
        </div>
      )}

      {/* ── Chat area ── */}
      <main className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-5">

        {/* Welcome banner + message */}
        <WelcomeBanner />
        <div className="flex items-start gap-2.5">
          <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center font-syne font-bold text-xs text-white flex-shrink-0 mt-0.5 shadow-[0_2px_8px_rgba(124,111,255,0.4)]">P</div>
          <div className="bg-s2 border border-border rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm leading-relaxed text-[#ececf5] max-w-lg">
            {WELCOME}
          </div>
        </div>

        {/* Messages */}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} msg={msg} />
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-start gap-2.5 animate-fade-up">
            <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center font-syne font-bold text-xs text-white flex-shrink-0 mt-0.5">P</div>
            <div className="bg-s2 border border-border rounded-2xl rounded-bl-sm px-4 py-2.5">
              <div className="flex gap-1.5 items-center py-0.5">
                {[0, 1, 2].map((i) => (
                  <span key={i} className="w-2 h-2 rounded-full bg-muted animate-blink"
                    style={{ animationDelay: `${i * 0.18}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* ── Suggestion chips ── */}
      {showSugg && (
        <div className="px-5 pb-3 flex flex-wrap gap-2 flex-shrink-0">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => handleSend(s)}
              className="bg-s2 border border-border text-muted text-xs font-dm px-3.5 py-1.5 rounded-full hover:border-accent hover:text-[#ececf5] hover:bg-[rgba(124,111,255,0.08)] transition-all animate-pop"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* ── Input bar ── */}
      <footer className="glass border-t border-border px-5 py-3.5 flex gap-3 flex-shrink-0">
        <input
          ref={inputRef}
          id="chat-input"
          className="flex-1 bg-s2 border border-border rounded-2xl text-[#ececf5] font-dm text-sm px-4 py-3 outline-none transition-all focus:border-accent focus:bg-s3 focus:shadow-[0_0_0_3px_rgba(124,111,255,0.12)] placeholder-muted2 disabled:opacity-50"
          placeholder="What are you looking for today?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
          autoFocus
        />
        <button
          id="send-btn"
          onClick={() => handleSend()}
          disabled={loading || !input.trim()}
          className="w-11 h-11 rounded-full gradient-bg flex items-center justify-center flex-shrink-0 hover:opacity-88 disabled:opacity-30 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95 shadow-[0_2px_12px_rgba(124,111,255,0.35)]"
          title="Send"
        >
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </footer>
    </div>
  );
}
