/** Animated capability banner shown above the first chat message */
const BADGES = [
  { icon: "🧠", label: "Claude AI", sub: "Intent + ranking" },
  { icon: "🔍", label: "FAISS Search", sub: "Semantic similarity" },
  { icon: "🛍️", label: "Shopify API", sub: "Live catalogue" },
];

export default function WelcomeBanner() {
  return (
    <div className="animate-fade-up mb-1">
      {/* Capability badges */}
      <div className="flex gap-2 flex-wrap justify-center mb-4">
        {BADGES.map((b, i) => (
          <div
            key={b.label}
            className="flex items-center gap-2 bg-s2 border border-border rounded-xl px-3 py-2 text-[12px] animate-pop"
            style={{ animationDelay: `${i * 0.08}s` }}
          >
            <span className="text-base">{b.icon}</span>
            <div>
              <div className="text-[#ececf5] font-semibold font-syne leading-tight">{b.label}</div>
              <div className="text-muted2 text-[10px]">{b.sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* How it works flow */}
      <div className="flex items-center gap-1 justify-center flex-wrap">
        {[
          { step: "1", text: "Type naturally" },
          { step: "2", text: "AI parses intent" },
          { step: "3", text: "Top picks + explanations" },
        ].map((s, i) => (
          <span key={s.step} className="flex items-center gap-1">
            <span className="flex items-center gap-1.5 bg-s3 border border-border rounded-full px-3 py-1 text-[11px] text-muted">
              <span className="w-4 h-4 rounded-full gradient-bg flex items-center justify-center text-white text-[9px] font-bold flex-shrink-0">
                {s.step}
              </span>
              {s.text}
            </span>
            {i < 2 && <span className="text-muted2 text-xs">→</span>}
          </span>
        ))}
      </div>
    </div>
  );
}
