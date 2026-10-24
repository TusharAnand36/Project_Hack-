import { screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";

import snapshot from "../../public/snapshots/pea_beverage.en.json";
import type { AnalyzeResponse } from "@/api/client";
import { DiagnosisScreen } from "@/screens/DiagnosisScreen";
import { VerdictScreen } from "@/screens/VerdictScreen";
import { useStore } from "@/store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/api/hooks", () => ({ useSources: () => new Map(), useDataFile: () => ({ data: undefined }) }));

const limits = [
  ["hexane_residue", "10"],
  ["aflatoxin_b1", "10"],
  ["total_aflatoxins", "15"],
  ["lead", "1"],
  ["cadmium", "0.1"],
  ["arsenic", "0.5"],
  ["mercury", "0.1"],
];

it.each(["verdict", "diagnosis"])("renders all seven project limits on %s", (page) => {
  useStore.setState({ request: null });
  const data = snapshot as unknown as AnalyzeResponse;
  renderWithProviders(page === "verdict" ? <VerdictScreen data={data} /> : <DiagnosisScreen data={data} />);
  for (const [compound, value] of limits) {
    const row = screen.getByTestId(`${page === "verdict" ? "safety" : "diag"}-${compound}`);
    const cells = within(row).getAllByRole("cell");
    const limitCell = page === "verdict" ? cells[0] : cells[4];
    expect(limitCell).toHaveTextContent(value);
    expect(row).toHaveTextContent(/not measured|no data/i);
  }
  expect(screen.getByText(/not independently verified regulatory limits/i)).toBeInTheDocument();
});
