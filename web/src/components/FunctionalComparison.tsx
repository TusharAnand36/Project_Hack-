import { useTranslation } from "react-i18next";
import type { AnalyzeResponse } from "@/api/client";

export function FunctionalComparison({ data }: { data: AnalyzeResponse }) {
  const { t } = useTranslation();
  const comparison = data.functional_comparison;
  if (!comparison.properties.length) return null;
  return (
    <section className="my-8" data-testid="functional-comparison">
      <p className="workspace-eyebrow">{t("functional.eyebrow")}</p>
      <h3 className="mt-2">{t("functional.title")}</h3>
      <p className="mb-4 mt-3 text-sm text-muted-foreground">{comparison.note}</p>
      <div className="overflow-x-auto" tabIndex={0}>
        <table className="w-full min-w-[48rem] text-sm">
          <caption className="sr-only">{t("functional.title")}</caption>
          <thead>
            <tr className="border-b border-border">
              <th className="p-3 text-start" scope="col">
                {t("functional.property")}
              </th>
              <th className="p-3 text-start" scope="col">
                {t("functional.flour")}
              </th>
              <th className="p-3 text-start" scope="col">
                {t("functional.extracted")}
              </th>
              <th className="p-3 text-start" scope="col">
                {t("functional.pea")}
              </th>
            </tr>
          </thead>
          <tbody>
            {comparison.properties.map((property) => (
              <tr className="border-b border-border align-top" key={property.id}>
                <th className="p-3 text-start font-medium" scope="row">
                  {property.name}
                </th>
                <td className="p-3">{property.oilseed_flour}</td>
                <td className="p-3">
                  {property.oilseed_isolate}
                  <p className="mt-2 text-xs text-muted-foreground">{property.oilseed_conditions}</p>
                </td>
                <td className="p-3">
                  {property.pea_isolate}
                  <p className="mt-2 text-xs text-muted-foreground">{property.pea_conditions}</p>
                  <details className="mt-3">
                    <summary className="min-h-9 cursor-pointer underline">
                      {t("functional.compareHow")}
                    </summary>
                    <p>{property.next_test}</p>
                    <p className="mt-2 text-xs">{property.evidence_status}</p>
                    <p className="text-xs">{property.source_ids.join(" · ")}</p>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-sm font-medium">{t("functional.noWinner")}</p>
      <p className="mt-3 text-sm">
        {t("functional.applicationTests")}: {comparison.application_tests.join(" · ")}
      </p>
      <a
        className="mt-3 inline-block min-h-9 underline underline-offset-4"
        href="https://doi.org/10.1016/j.fochx.2025.102898"
        target="_blank"
        rel="noreferrer"
      >
        {t("functional.paper")}
      </a>
    </section>
  );
}
