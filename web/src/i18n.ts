import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import en from "./locales/en.json";
import hi from "./locales/hi.json";

const SUPPORTED = ["en", "hi"] as const;

function initialLanguage(): string {
  try {
    const saved = localStorage.getItem("lang");
    if (saved && (SUPPORTED as readonly string[]).includes(saved)) return saved;
  } catch {
    /* storage blocked: fall through */
  }
  return navigator.language?.toLowerCase().startsWith("hi") ? "hi" : "en";
}

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, hi: { translation: hi } },
  lng: initialLanguage(),
  fallbackLng: "en", // Hindi strings arrive in Phase 7; missing keys fall back to English.
  interpolation: { escapeValue: false },
});

i18n.on("languageChanged", (lng) => {
  document.documentElement.lang = lng;
});
document.documentElement.lang = i18n.language;

export default i18n;
