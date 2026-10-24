import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api, type AnalyzeResponse } from "@/api/client";
import { Button } from "./ui/button";

const field = "mt-1 block min-h-11 w-full rounded-md border border-border bg-background px-3";

export function FeedbackForm({ data, disabled }: { data: AnalyzeResponse; disabled: boolean }) {
  const { t } = useTranslation();
  const [helpful, setHelpful] = useState("yes");
  const [outcome, setOutcome] = useState<"not_tested" | "worked" | "failed">("not_tested");
  const [issue, setIssue] = useState<
    "none" | "solubility" | "texture" | "sensory" | "cost" | "yield" | "safety"
  >("none");
  const [chain, setChain] = useState("");
  const [notes, setNotes] = useState("");
  const mutation = useMutation({
    mutationFn: () =>
      api.feedback({
        case_id: data.case_id!,
        helpful: helpful === "yes",
        outcome,
        issue,
        chain_id: chain || null,
        notes,
      }),
  });
  const context = mutation.data?.context ?? data.feedback_context;
  return (
    <aside className="no-print mt-10 border-t border-border pt-7" data-testid="case-feedback">
      <p className="workspace-eyebrow">{t("feedback.eyebrow")}</p>
      <h3 className="mt-2">{t("feedback.title")}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{t("feedback.scope")}</p>
      {context.count > 0 && (
        <div className="my-4 border-l-2 border-primary pl-4 text-sm">
          <p>{t("feedback.previous", { count: context.count })}</p>
          <ul className="list-disc ps-5">
            {context.observations.map((observation) => (
              <li key={observation}>{observation}</li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-muted-foreground">{context.note}</p>
        </div>
      )}
      {!data.case_id || disabled ? (
        <p className="mt-4 text-sm text-muted-foreground">{t("feedback.liveRequired")}</p>
      ) : mutation.isSuccess ? (
        <p className="mt-4 text-sm" role="status">
          {t("feedback.saved")}
        </p>
      ) : (
        <form
          className="mt-5 grid gap-4 sm:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            mutation.mutate();
          }}
        >
          <label className="text-sm">
            {t("feedback.helpful")}
            <select className={field} value={helpful} onChange={(e) => setHelpful(e.target.value)}>
              <option value="yes">{t("input.yes")}</option>
              <option value="no">{t("input.no")}</option>
            </select>
          </label>
          <label className="text-sm">
            {t("feedback.outcome")}
            <select
              className={field}
              value={outcome}
              onChange={(e) => setOutcome(e.target.value as typeof outcome)}
            >
              {["not_tested", "worked", "failed"].map((o) => (
                <option key={o} value={o}>
                  {t(`feedback.outcomes.${o}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            {t("feedback.chain")}
            <select className={field} value={chain} onChange={(e) => setChain(e.target.value)}>
              <option value="">{t("feedback.wholeCase")}</option>
              {data.chains.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.steps.join(" → ") || t("chains.rawFlour")}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            {t("feedback.issue")}
            <select
              className={field}
              value={issue}
              onChange={(e) => setIssue(e.target.value as typeof issue)}
            >
              {["none", "solubility", "texture", "sensory", "cost", "yield", "safety"].map((o) => (
                <option key={o} value={o}>
                  {t(`feedback.issues.${o}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm sm:col-span-2">
            {t("feedback.notes")}
            <textarea
              className={field + " py-3"}
              rows={3}
              maxLength={1500}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </label>
          <p className="text-xs text-muted-foreground sm:col-span-2">{t("feedback.privacy")}</p>
          {mutation.isError && (
            <p role="alert" className="text-sm text-bad sm:col-span-2">
              {(mutation.error as Error).message}
            </p>
          )}
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? t("state.loading") : t("feedback.submit")}
          </Button>
        </form>
      )}
    </aside>
  );
}
