/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  future: { hoverOnlyWhenSupported: true },
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Arial", '"Noto Sans Devanagari"', "Helvetica", "sans-serif"] },
      colors: {
        border: "hsl(var(--border) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        surface: "hsl(var(--surface) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
        tag: {
          measured: "hsl(var(--tag-m) / <alpha-value>)",
          published: "hsl(var(--tag-p) / <alpha-value>)",
          assumed: "hsl(var(--tag-a) / <alpha-value>)",
          synthetic: "hsl(var(--tag-s) / <alpha-value>)",
        },
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        ok: "hsl(var(--ok) / <alpha-value>)",
        warn: "hsl(var(--warn) / <alpha-value>)",
        bad: "hsl(var(--bad) / <alpha-value>)",
      },
      borderRadius: { lg: "var(--radius)", md: "calc(var(--radius) - 2px)", sm: "calc(var(--radius) - 4px)" },
    },
  },
  plugins: [],
};
