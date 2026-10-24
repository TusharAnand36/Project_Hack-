import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";

import { useStore } from "@/store";
import { renderWithProviders } from "@/test/render";
import { InputScreen } from "./InputScreen";

vi.mock("@/api/hooks", () => ({
  usePresets: () => ({ data: [], isPending: false }),
  useDataFile: () => ({ data: undefined }),
  useDataReport: () => ({ data: undefined }),
}));

it("shows plain form labels and all seven contaminant inputs without provenance badges", async () => {
  useStore.setState({ request: null });
  const { container } = renderWithProviders(<InputScreen />);
  expect(screen.queryByText("default", { exact: true })).not.toBeInTheDocument();
  await userEvent.type(screen.getByLabelText("Minimum protein in the ingredient (%)"), "40");
  expect(container.querySelector("form label [title]")).toBeNull();
  await userEvent.click(container.querySelector("summary")!);
  for (const name of [
    "Hexane residue (mg/kg)",
    "Aflatoxin B1 (µg/kg)",
    "Total aflatoxins: B1+B2+G1+G2 (µg/kg)",
    "Lead (mg/kg)",
    "Cadmium (mg/kg)",
    "Arsenic, total (mg/kg)",
    "Mercury (mg/kg)",
  ]) {
    expect(screen.getByLabelText(name, { exact: true })).toBeVisible();
  }
});
