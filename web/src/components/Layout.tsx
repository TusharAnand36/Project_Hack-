import { useTranslation } from "react-i18next";

import { useHealth } from "@/api/hooks";
import { CompassMark } from "@/components/Brand";
import { cn } from "@/lib/utils";
import { SCREENS, useStore } from "@/store";

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
    <header className="workspace-header no-print">
      <div className="workspace-header-inner">
        <div>
          <h1>
            <a href="#/" className="site-brand" aria-label={t("site.homeLabel")}>
              <CompassMark />
              <span>
                upcycle<span className="brand-second">compass</span>
              </span>
            </a>
          </h1>
        </div>
        <a href="#/" className="workspace-home-link">
          <span aria-hidden="true">↖</span>
          {t("site.backHome")}
        </a>
        <div className="workspace-tools">
          <span
            role="status"
            className={cn(
              "workspace-health",
              ok ? "text-ok" : health.isPending ? "text-muted-foreground" : "text-bad",
            )}
            data-testid="health"
          >
            {t("health.label")}: {t(health.isPending ? "health.checking" : ok ? "health.ok" : "health.down")}
          </span>
          <label className="workspace-source-toggle">
            <input type="checkbox" className="h-5 w-5" checked={showSources} onChange={toggle} />
            {t("app.showSources")}
          </label>
          <label className="workspace-language">
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
    <nav aria-label={t("nav.label")} className="workspace-stepper hidden md:block">
      <ol>
        {SCREENS.map((s, i) => (
          <li key={s}>
            <button
              type="button"
              onClick={() => setScreen(s)}
              disabled={disabled && s !== "input"}
              aria-current={screen === s ? "page" : undefined}
              className="workspace-step"
              data-testid={`nav-${s}`}
            >
              <span className="workspace-step-number" aria-hidden="true">
                0{i + 1}
              </span>
              {t(`nav.${s}`)}
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
      className="workspace-bottom-nav fixed inset-x-0 bottom-0 z-40 border-t border-border bg-background md:hidden"
    >
      <ul className="grid grid-cols-6">
        {SCREENS.map((s, i) => (
          <li key={s}>
            <button
              type="button"
              onClick={() => setScreen(s)}
              disabled={disabled && s !== "input"}
              aria-current={screen === s ? "page" : undefined}
              className="workspace-mobile-step"
              data-testid={`tab-${s}`}
            >
              <span aria-hidden="true" className="workspace-step-number">
                {i + 1}
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
    <footer className="workspace-footer text-muted-foreground">
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
