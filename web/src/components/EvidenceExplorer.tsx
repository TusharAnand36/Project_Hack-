import { useTranslation } from "react-i18next";
import { useDataFile } from "@/api/hooks";
import { useStore } from "@/store";

type Evidence = { note: string; records: { section: string; fields: Record<string, string> }[] };

export function EvidenceExplorer() {
  const { t } = useTranslation();
  const material = useStore((s) => s.request?.byproduct?.split("_")[0] ?? "");
  const data = useDataFile<Evidence>("research_evidence");
  const rows =
    data.data?.records.filter(
      (record) =>
        ["Read me", "Research gaps", "Prototype mapping"].includes(record.section) ||
        Object.values(record.fields).some((value) => value.toLowerCase().includes(material)),
    ) ?? [];
  return (
    <details className="my-6 border-t border-border pt-4">
      <summary className="min-h-11 cursor-pointer font-medium">{t("workflow.evidenceExplorer")}</summary>
      <p className="my-3 text-sm text-muted-foreground">{data.data?.note ?? t("workflow.notEstimated")}</p>
      {rows.map((record, index) => (
        <details className="border-t border-border py-3 text-sm" key={`${record.section}-${index}`}>
          <summary className="min-h-9 cursor-pointer">
            {record.section} · {Object.values(record.fields).slice(0, 2).join(" · ")}
          </summary>
          <dl className="grid gap-2 py-3 sm:grid-cols-[12rem_1fr]">
            {Object.entries(record.fields).map(([key, value]) => (
              <div key={key} className="contents">
                <dt className="font-medium">{key}</dt>
                <dd className="text-muted-foreground">{value}</dd>
              </div>
            ))}
          </dl>
        </details>
      ))}
    </details>
  );
}
