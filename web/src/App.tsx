import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import type { AnalyzeResponse } from "@/api/client";
import { useAnalysis } from "@/api/hooks";
import { BottomBar, Footer, SafetyNote, Stepper, TopBar } from "@/components/Layout";
import { ErrorCard, LoadingScreen } from "@/components/States";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { FeedbackForm } from "@/components/FeedbackForm";
import { InputScreen } from "@/screens/InputScreen";
import { VerdictScreen } from "@/screens/VerdictScreen";
import { useStore } from "@/store";
import "./workspace.css";

// screens with charts and tables load on first use (bundle budget, website plan Phase 8)
const named = <K extends string>(
  p: Promise<Record<K, React.ComponentType<{ data: AnalyzeResponse }>>>,
  k: K,
) => p.then((m) => ({ default: m[k] }));
const DiagnosisScreen = lazy(() => named(import("@/screens/DiagnosisScreen"), "DiagnosisScreen"));
const ChainsScreen = lazy(() => named(import("@/screens/ChainsScreen"), "ChainsScreen"));
const CostScreen = lazy(() => named(import("@/screens/CostScreen"), "CostScreen"));
const NextScreen = lazy(() => named(import("@/screens/NextScreen"), "NextScreen"));
const MemoScreen = lazy(() => named(import("@/screens/MemoScreen"), "MemoScreen"));

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
    window.scrollTo({ top: 0, behavior: "instant" });
    mainRef.current?.focus({ preventScroll: true });
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
      memo: <MemoScreen data={d} />,
    }[screen];
  }

  return (
    <div className="compass-app min-h-screen">
      <a
        href="#main"
        onClick={(event) => {
          event.preventDefault();
          mainRef.current?.focus();
        }}
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-background focus:p-2"
      >
        {t("app.skip")}
      </a>
      <TopBar />
      <Stepper disabled={!request} />
      <SafetyNote />
      <main id="main" ref={mainRef} tabIndex={-1} className="workspace-main outline-none">
        {result?.offline && screen !== "input" && (
          <p
            role="status"
            className="mb-4 rounded-md border border-warn px-3 py-2 text-sm text-warn"
            data-testid="offline-badge"
          >
            {t("state.errorSnapshot")} · {t("app.offline")}
            {result.data.snapshot &&
              ` · ${t("app.snapshotStamp", { date: result.data.snapshot.generated_at.slice(0, 16).replace("T", " "), dataset: result.data.snapshot.dataset_version })}`}
          </p>
        )}
        {analysis.isFetching && result && screen !== "input" && (
          <p className="mb-2 text-xs text-muted-foreground">{t("state.loading")}</p>
        )}
        {result && screen !== "input" && (
          <p className="mb-5 border-l-2 border-primary pl-4 text-xs text-muted-foreground">
            {t("workflow.legend")}
          </p>
        )}
        <Suspense fallback={<LoadingScreen />}>{body}</Suspense>
        {result && screen !== "input" && screen !== "memo" && (
          <FeedbackForm
            key={result.data.case_id ?? "offline"}
            data={result.data}
            disabled={result.offline || analysis.isFetching || analysis.isError}
          />
        )}
      </main>
      <div aria-live="polite" className="sr-only">
        {announce}
      </div>
      <Footer />
      <BottomBar disabled={!request} />
    </div>
  );
}
