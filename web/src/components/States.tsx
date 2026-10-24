import { useTranslation } from "react-i18next";

import { Button } from "./ui/button";
import { Card, Skeleton } from "./ui/card";

export function LoadingScreen() {
  const { t } = useTranslation();
  return (
    <div role="status" aria-live="polite" className="space-y-3">
      <span className="sr-only">{t("state.loading")}</span>
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-16 w-full" />
      <Skeleton className="h-16 w-2/3" />
    </div>
  );
}

export function ErrorCard({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { t } = useTranslation();
  return (
    <Card role="alert" className="border-bad">
      <p className="font-medium text-bad">{t("state.error")}</p>
      <p className="text-sm text-muted-foreground">{message}</p>
      {onRetry && (
        <Button variant="outline" className="mt-3" onClick={onRetry}>
          {t("state.retry")}
        </Button>
      )}
    </Card>
  );
}

export function ScreenHeader({
  title,
  summary,
  eyebrow,
  accent,
}: {
  title: string;
  summary: string;
  eyebrow?: string;
  accent?: string;
}) {
  return (
    <header className="workspace-screen-header">
      {eyebrow && <p className="workspace-eyebrow">{eyebrow}</p>}
      <h2>
        {title}
        {accent && (
          <>
            <br />
            <em>{accent}</em>
            <span className="workspace-dot">.</span>
          </>
        )}
      </h2>
      <p className="workspace-summary">{summary}</p>
    </header>
  );
}
