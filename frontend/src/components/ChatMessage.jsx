import ProductCard from "./ProductCard";
import SkeletonCard from "./SkeletonCard";

function IntentPills({ intent }) {
  if (!intent) return null;
  const chips = [];
  if (intent.category)   chips.push({ label: intent.category, color: "accent" });
  if (intent.budget_max) chips.push({ label: `under ₹${Number(intent.budget_max).toLocaleString("en-IN")}`, color: "accent2" });
  if (intent.recipient)  chips.push({ label: `for ${intent.recipient}`, color: "accent" });
  if (intent.gender)     chips.push({ label: intent.gender, color: "accent" });
  (intent.preferences || []).slice(0, 2).forEach((p) => chips.push({ label: p, color: "accent2" }));
  if (!chips.length) return null;

  return (
    <div className="flex flex-wrap gap-1.5 mb-1.5">
      {chips.map((c) => (
        <span
          key={c.label}
          className={`text-[11px] px-2.5 py-0.5 rounded-full border animate-pop ${
            c.color === "accent2"
              ? "text-accent2 bg-[rgba(0,223,168,0.1)] border-[rgba(0,223,168,0.2)]"
              : "text-accent  bg-[rgba(124,111,255,0.1)] border-[rgba(124,111,255,0.2)]"
          }`}
        >
          {c.label}
        </span>
      ))}
    </div>
  );
}

function Avatar() {
  return (
    <div className="w-8 h-8 rounded-full gradient-bg flex items-center justify-center font-syne font-bold text-xs text-white flex-shrink-0 mt-0.5 shadow-[0_2px_8px_rgba(124,111,255,0.4)]">
      P
    </div>
  );
}

export default function ChatMessage({ msg }) {
  if (msg.type === "user") {
    return (
      <div className="flex justify-end animate-fade-up">
        <div className="bg-accent text-white rounded-2xl rounded-br-sm px-4 py-2.5 max-w-[70%] text-sm leading-relaxed shadow-[0_2px_12px_rgba(124,111,255,0.2)]">
          {msg.text}
        </div>
      </div>
    );
  }

  if (msg.type === "error") {
    return (
      <div className="flex items-start gap-2.5 animate-fade-up">
        <div className="w-8 h-8 rounded-full bg-accent3 flex items-center justify-center text-white font-syne font-bold text-xs flex-shrink-0 mt-0.5">!</div>
        <div className="bg-[rgba(255,95,95,0.08)] border border-[rgba(255,95,95,0.25)] text-accent3 rounded-2xl px-4 py-2.5 text-sm max-w-lg">
          {msg.text}
        </div>
      </div>
    );
  }

  // Skeleton loading state (shown as a separate message type by App.jsx)
  if (msg.type === "skeleton") {
    return (
      <div className="flex items-start gap-2.5 animate-fade-up">
        <Avatar />
        <div className="flex flex-col gap-2 flex-1 max-w-full">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-1">
            {[0, 1, 2].map((i) => <SkeletonCard key={i} />)}
          </div>
        </div>
      </div>
    );
  }

  // Agent response
  return (
    <div className="flex items-start gap-2.5 animate-fade-up">
      <Avatar />
      <div className="flex flex-col gap-2 flex-1 max-w-full">
        <IntentPills intent={msg.intent} />

        <div className="flex items-start gap-2 flex-wrap">
          <div className="bg-s2 border border-border rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm leading-relaxed text-[#ececf5] max-w-lg">
            {msg.text}
          </div>
          {msg.responseTime && (
            <span className="text-[10px] text-muted2 mt-auto pb-1 self-end">
              ⚡ {msg.responseTime}ms
            </span>
          )}
        </div>

        {msg.products?.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-1">
            {msg.products.map((p, i) => (
              <ProductCard key={p.id} product={p} rank={i} />
            ))}
          </div>
        )}

        {msg.followup && (
          <div className="flex items-center gap-2 border-l-2 border-accent bg-[rgba(124,111,255,0.06)] rounded-r-xl px-3.5 py-2.5 max-w-lg mt-0.5">
            <span className="text-accent text-base flex-shrink-0">💬</span>
            <span className="text-[#ececf5] text-[13px] leading-relaxed">{msg.followup}</span>
          </div>
        )}
      </div>
    </div>
  );
}
