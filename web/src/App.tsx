import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import { useAnalysis } from "@/api/hooks";
import { BottomBar, Footer, Stepper, TopBar } from "@/components/Layout";
import { ErrorCard, LoadingScreen } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ChainsScreen } from "@/screens/ChainsScreen";
import { CostScreen } from "@/screens/CostScreen";
import { DiagnosisScreen } from "@/screens/DiagnosisScreen";
import { InputScreen } from "@/screens/InputScreen";
import { NextScreen } from "@/screens/NextScreen";
import { VerdictScreen } from "@/screens/VerdictScreen";
import { useStore } from "@/store";

export default function App() {
  const { t } = useTranslation();
  const screen = useStore((s) => s.screen);
  const request = useStore((s) => s.request);
  const setScreen = useStore((s) => s.setScreen);
  const analysis = useAnalysis();
  const mainRef = useRef<HTMLElement>(null);
  const [announce, setAnnounce] = useState("");

  // move focus to the new screen and announce updates (WCAG: live regions, focus management)
  useEffect(() => {
    mainRef.current?.focus();
  }, [screen]);
  useEffect(() => {
    if (analysis.data) setAnnounce(t("app.analysisUpdated"));
  }, [analysis.data, analysis.dataUpdatedAt, t]);

  const result = analysis.data;
  let body;
  if (screen === "input") body = <InputScreen />;
  else if (!request)
    body = (
      <Card>
        <p>{t("app.needInput")}</p>
        <Button className="mt-3" onClick={() => setScreen("input")}>
          {t("app.goToInput")}
        </Button>
      </Card>
    );
  else if (analysis.isError && !result)
    body = <ErrorCard message={(analysis.error as Error).message} onRetry={() => void analysis.refetch()} />;
  else if (!result) body = <LoadingScreen />;
  else {
    const d = result.data;
    body = {
      verdict: <VerdictScreen data={d} />,
      diagnosis: <DiagnosisScreen data={d} />,
      chains: <ChainsScreen data={d} />,
      cost: <CostScreen data={d} />,
      next: <NextScreen data={d} />,
    }[screen];
  }

  return (
    <div className="min-h-screen">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-background focus:p-2"
      >
        {t("app.skip")}
      </a>
      <TopBar />
      <Stepper disabled={!request} />
      <main id="main" ref={mainRef} tabIndex={-1} className="mx-auto max-w-6xl px-4 py-6 outline-none">
        {result?.offline && screen !== "input" && (
          <p
            role="status"
            className="mb-4 rounded-md border border-warn px-3 py-2 text-sm text-warn"
            data-testid="offline-badge"
          >
            {t("state.errorSnapshot")} · {t("app.offline")}
          </p>
        )}
        {analysis.isFetching && result && screen !== "input" && (
          <p className="mb-2 text-xs text-muted-foreground">{t("state.loading")}</p>
        )}
        {body}
      </main>
      <div aria-live="polite" className="sr-only">
        {announce}
      </div>
      <Footer />
      <BottomBar disabled={!request} />
    </div>
  );
}
