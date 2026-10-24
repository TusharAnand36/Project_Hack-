import { useTranslation } from "react-i18next";

import { useHealth } from "@/api/hooks";
import { cn } from "@/lib/utils";
import { SCREENS, useStore, type Screen } from "@/store";

const MOBILE: Screen[] = ["input", "verdict", "chains", "cost", "next"];
const ICON: Record<Screen, string> = {
  input: "✎",
  verdict: "⚑",
  diagnosis: "⚗",
  chains: "⛓",
  cost: "₹",
  next: "→",
  memo: "🖨",
};

export function TopBar() {
  const { t, i18n } = useTranslation();
  const showSources = useStore((s) => s.showSources);
  const toggle = useStore((s) => s.toggleSources);
  const health = useHealth();
  const ok = health.data?.status === "ok";
  const setLang = (lng: string) => {
    void i18n.changeLanguage(lng);
    try {
      localStorage.setItem("lang", lng);
    } catch {
      /* storage blocked */
    }
  };
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-2">
        <div className="me-auto">
          <h1 className="text-lg font-semibold leading-tight">
            <span aria-hidden="true">🧭 </span>
            {t("app.title")}
          </h1>
          <p className="text-xs text-muted-foreground">{t("app.tagline")}</p>
        </div>
        <span
          role="status"
          className={cn("text-xs", ok ? "text-ok" : health.isPending ? "text-muted-foreground" : "text-bad")}
          data-testid="health"
        >
          {t("health.label")}: {t(health.isPending ? "health.checking" : ok ? "health.ok" : "health.down")}
        </span>
        <label className="flex min-h-11 items-center gap-2 text-sm">
          <input type="checkbox" className="h-5 w-5" checked={showSources} onChange={toggle} />
          {t("app.showSources")}
        </label>
        <label className="text-sm">
          <span className="sr-only">{t("app.language")}</span>
          <select
            className="min-h-11 rounded-md border border-border bg-background px-2"
            value={i18n.language}
            onChange={(e) => setLang(e.target.value)}
            aria-label={t("app.language")}
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
          </select>
        </label>
      </div>
    </header>
  );
}

/** Shown in Hindi: safety wording stays in English until a Hindi reader has reviewed it. */
export function SafetyNote() {
  const { t, i18n } = useTranslation();
  if (i18n.language !== "hi") return null;
  return (
    <p className="mx-auto max-w-6xl px-4 pt-2 text-xs text-muted-foreground" data-testid="safety-note">
      {t("app.safetyEnglish")}
    </p>
  );
}

export function Stepper({ disabled }: { disabled: boolean }) {
  const { t } = useTranslation();
  const screen = useStore((s) => s.screen);
  const setScreen = useStore((s) => s.setScreen);
  return (
    <nav aria-label={t("nav.label")} className="hidden border-b border-border md:block">
      <ol className="mx-auto flex max-w-6xl gap-1 px-4">
        {SCREENS.map((s, i) => (
          <li key={s}>
            <button
              type="button"
              onClick={() => setScreen(s)}
              disabled={disabled && s !== "input"}
              aria-current={screen === s ? "page" : undefined}
              className={cn(
                "min-h-11 border-b-2 px-3 text-sm disabled:opacity-40",
                screen === s ? "border-primary font-semibold" : "border-transparent hover:border-border",
              )}
              data-testid={`nav-${s}`}
            >
              {i + 1}. {t(`nav.${s}`)}
            </button>
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function BottomBar({ disabled }: { disabled: boolean }) {
  const { t } = useTranslation();
  const screen = useStore((s) => s.screen);
  const setScreen = useStore((s) => s.setScreen);
  return (
    <nav
      aria-label={t("nav.label")}
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background md:hidden"
    >
      <ul className="grid grid-cols-5">
        {MOBILE.map((s) => (
          <li key={s}>
            <button
              type="button"
              onClick={() => setScreen(s)}
              disabled={disabled && s !== "input"}
              aria-current={screen === s ? "page" : undefined}
              className={cn(
                "flex min-h-14 w-full flex-col items-center justify-center text-xs disabled:opacity-40",
                screen === s ? "font-semibold text-primary" : "text-muted-foreground",
              )}
              data-testid={`tab-${s}`}
            >
              <span aria-hidden="true" className="text-base">
                {ICON[s]}
              </span>
              {t(`nav.${s}`)}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export function Footer() {
  const { t } = useTranslation();
  const setScreen = useStore((s) => s.setScreen);
  return (
    <footer className="mx-auto max-w-6xl border-t border-border px-4 pb-24 pt-4 text-sm text-muted-foreground md:pb-6">
      <p>{t("footer.disclaimer")}</p>
      <p>{t("footer.poc")}</p>
      <p>{t("footer.privacy")}</p>
      <div className="mt-1 flex flex-wrap gap-4">
        <button type="button" className="min-h-9 underline" onClick={() => setScreen("next")}>
          {t("footer.limitations")}
        </button>
        <a
          className="inline-flex min-h-9 items-center underline"
          href="/open-data-pack.zip"
          download
          data-testid="data-pack"
        >
          {t("footer.dataPack")}
        </a>
      </div>
    </footer>
  );
}
