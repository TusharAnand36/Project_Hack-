import { useTranslation } from "react-i18next";

import { HealthIndicator } from "@/components/HealthIndicator";

export default function App() {
  const { t } = useTranslation();
  return (
    <div className="mx-auto flex min-h-screen max-w-3xl flex-col px-4">
      <a href="#main" className="sr-only focus:not-sr-only focus:p-2">
        {t("app.skip")}
      </a>
      <header className="border-b border-border py-4">
        <h1 className="text-xl font-semibold">{t("app.title")}</h1>
        <p className="text-muted-foreground">{t("app.tagline")}</p>
      </header>
      <main id="main" className="flex-1 py-6">
        <HealthIndicator />
      </main>
      <footer className="border-t border-border py-4 text-sm text-muted-foreground">
        <p>{t("footer.disclaimer")}</p>
        <p>{t("footer.poc")}</p>
      </footer>
    </div>
  );
}
