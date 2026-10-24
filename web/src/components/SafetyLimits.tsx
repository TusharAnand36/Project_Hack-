import { useTranslation } from "react-i18next";

import type { Gate } from "@/api/client";
import { Num } from "@/components/Num";

export function SafetyLimits({ gates }: { gates: Gate[] }) {
  const { t } = useTranslation();
  const checks = gates.flatMap((g) => g.checks ?? []);
  return (
    <section className="mt-6" aria-labelledby="safety-limits-title" data-testid="safety-limits">
      <h3 id="safety-limits-title">{t("safety.title")}</h3>
      <p className="mb-3 mt-2 text-sm text-muted-foreground">{t("safety.policy")}</p>
      <div className="overflow-x-auto" tabIndex={0}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th scope="col" className="py-3 pe-4 text-start">
                {t("diagnosis.compound")}
              </th>
              <th scope="col" className="pe-4 text-start">
                {t("verdict.limit")}
              </th>
              <th scope="col" className="pe-4 text-start">
                {t("verdict.measured")}
              </th>
              <th scope="col" className="text-start">
                {t("safety.status")}
              </th>
            </tr>
          </thead>
          <tbody>
            {checks.map((check) => (
              <tr
                key={check.compound}
                className="border-b border-border align-top"
                data-testid={`safety-${check.compound}`}
              >
                <th scope="row" className="py-3 pe-4 text-start font-medium">
                  {check.name}
                </th>
                <td className="py-3 pe-4 whitespace-nowrap">
                  ≤ <Num v={check.limit} />
                </td>
                <td className="py-3 pe-4">
                  {check.measured ? <Num v={check.measured} /> : t("diagnosis.noData")}
                </td>
                <td className="py-3">
                  <strong>{t(`verdict.gateState.${check.state}`)}</strong>
                  <p className="mt-1 max-w-md text-xs text-muted-foreground">{check.note}</p>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">{t("safety.units")}</p>
    </section>
  );
}
