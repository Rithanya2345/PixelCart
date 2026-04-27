import { useState } from "react";

/** Derive a 4.0–4.9 star rating from price for demo realism */
function starRating(price) {
  const n = Number(price);
  if (n >= 2000) return 4.8;
  if (n >= 1200) return 4.6;
  if (n >= 700)  return 4.3;
  return 4.1;
}

function Stars({ rating }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  return (
    <div className="flex items-center gap-0.5">
      {[...Array(full)].map((_, i) => (
        <svg key={i} width="10" height="10" viewBox="0 0 24 24" fill="#f59e0b"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
      ))}
      {half && (
        <svg width="10" height="10" viewBox="0 0 24 24"><defs><linearGradient id="h"><stop offset="50%" stopColor="#f59e0b"/><stop offset="50%" stopColor="#374151"/></linearGradient></defs><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" fill="url(#h)"/></svg>
      )}
      <span className="text-[10px] text-muted ml-0.5">{rating.toFixed(1)}</span>
    </div>
  );
}

export default function ProductCard({ product, rank = 0 }) {
  const [imgErr, setImgErr] = useState(false);
  const price  = Number(product.price).toLocaleString("en-IN");
  const rating = starRating(product.price);
  const isTopPick = rank === 0;

  return (
    <div
      className="glow-border card-hover bg-s3 border border-border rounded-2xl overflow-hidden flex flex-col animate-slide-in"
      style={{ animationDelay: `${rank * 0.06}s` }}
    >
      {/* Image */}
      <div className="relative h-48 bg-s4 flex-shrink-0 overflow-hidden">
        {product.image && !imgErr ? (
          <img
            src={product.image}
            alt={product.title}
            className="w-full h-full object-cover transition-transform duration-400 hover:scale-108"
            loading="lazy"
            onError={() => setImgErr(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-4xl text-muted2">🛍️</div>
        )}

        {/* Badges */}
        <div className="absolute top-2 left-2 flex gap-1">
          {isTopPick && (
            <span className="bg-gradient-to-r from-[#7c6fff] to-[#00dfa8] text-white text-[9px] font-bold px-2 py-0.5 rounded-full shadow-lg">
              🏆 AI Pick
            </span>
          )}
        </div>
        {product.in_stock === false && (
          <span className="absolute top-2 right-2 bg-accent3 text-white text-[9px] px-2 py-0.5 rounded-full">
            Out of stock
          </span>
        )}
      </div>

      {/* Info */}
      <div className="p-3 flex flex-col gap-1.5 flex-1">
        <p className="font-syne font-bold text-[13px] text-[#ececf5] leading-tight line-clamp-2">
          {product.title}
        </p>

        <div className="flex items-center justify-between">
          <p className="text-accent2 text-base font-semibold">₹{price}</p>
          <Stars rating={rating} />
        </div>

        {product.explanation && (
          <p className="text-muted text-[11.5px] leading-relaxed flex-1 border-l-2 border-[rgba(124,111,255,0.3)] pl-2">
            {product.explanation}
          </p>
        )}

        {/* Tags */}
        {product.tags?.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-0.5">
            {product.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="text-accent bg-[rgba(124,111,255,0.1)] text-[9px] px-2 py-0.5 rounded-full"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* CTA */}
        <a
          href={product.url || "#"}
          target="_blank"
          rel="noreferrer"
          className="gradient-bg text-white text-[11px] font-semibold text-center py-2 rounded-xl mt-2 block hover:opacity-85 transition-all duration-200 hover:shadow-[0_4px_12px_rgba(124,111,255,0.35)]"
        >
          {product.url && product.url !== "#" ? "View on Shopify →" : "View product →"}
        </a>
      </div>
    </div>
  );
}
