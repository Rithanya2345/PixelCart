/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        syne:   ["Syne", "sans-serif"],
        dm:     ["DM Sans", "sans-serif"],
        outfit: ["Outfit", "sans-serif"],
      },
      colors: {
        bg:      "#08080f",
        surface: "#101018",
        s2:      "#181824",
        s3:      "#1f1f2e",
        s4:      "#272738",
        border:  "#28283c",
        border2: "#383852",
        accent:  "#7c6fff",
        accent2: "#00dfa8",
        accent3: "#ff5f5f",
        muted:   "#7878a0",
        muted2:  "#44445a",
      },
      animation: {
        "fade-up":   "fadeUp .25s ease both",
        "blink":     "blink 1.3s infinite",
        "spin-slow": "spin 1s linear infinite",
        "shimmer":   "shimmer 1.6s infinite",
        "slide-in":  "slideIn .3s ease both",
        "pop":       "pop .2s ease both",
        "pulse-soft":"pulseSoft 2s ease-in-out infinite",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: 0, transform: "translateY(10px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        blink: {
          "0%,100%": { opacity: 0.2, transform: "scale(0.75)" },
          "50%":     { opacity: 1,   transform: "scale(1)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-400px 0" },
          "100%": { backgroundPosition: "400px 0" },
        },
        slideIn: {
          "0%":   { opacity: 0, transform: "translateY(16px) scale(0.97)" },
          "100%": { opacity: 1, transform: "translateY(0) scale(1)" },
        },
        pop: {
          "0%":   { transform: "scale(0.9)", opacity: 0 },
          "60%":  { transform: "scale(1.04)" },
          "100%": { transform: "scale(1)", opacity: 1 },
        },
        pulseSoft: {
          "0%,100%": { opacity: 1 },
          "50%":     { opacity: 0.55 },
        },
      },
    },
  },
  plugins: [],
};
