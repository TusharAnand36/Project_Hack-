import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import hi from "./locales/hi.json";

const SUPPORTED = ["en", "hi"] as const;
const DEVANAGARI_FONT =
  "https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&display=swap";

function initialLanguage(): string {
  try {
    const saved = localStorage.getItem("lang");
    if (saved && (SUPPORTED as readonly string[]).includes(saved)) return saved;
  } catch {
    /* storage blocked: fall through */
  }
  return navigator.language?.toLowerCase().startsWith("hi") ? "hi" : "en";
}

/** The Devanagari font is only downloaded when Hindi is in use (website plan §7.3). */
function ensureFont(lng: string) {
  if (lng !== "hi" || document.getElementById("font-devanagari")) return;
  const link = document.createElement("link");
  link.id = "font-devanagari";
  link.rel = "stylesheet";
  link.href = DEVANAGARI_FONT;
  document.head.appendChild(link);
}

function applyLanguage(lng: string) {
  document.documentElement.lang = lng;
  ensureFont(lng);
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi } },
  lng: initialLanguage(),
  // Safety wording is kept in English until reviewed (locales/review.json): missing Hindi keys fall back to English.
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

i18n.on("languageChanged", applyLanguage);
applyLanguage(i18n.language);

export default i18n;
