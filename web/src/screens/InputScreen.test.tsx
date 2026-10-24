import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import applications from "../../../data/applications.json";
import presets from "../../../data/presets.json";

import { useStore } from "@/store";
import { renderWithProviders } from "@/test/render";
import { InputScreen } from "./InputScreen";

vi.mock("@/api/hooks", () => ({
  usePresets: () => ({ data: presets.presets, isPending: false }),
  useDataFile: (name: string) => ({ data: name === "applications" ? applications : undefined }),
  useDataReport: () => ({ data: undefined }),
}));

it("shows plain form labels and all seven contaminant inputs without provenance badges", async () => {
  useStore.setState({ request: null });
  const { container } = renderWithProviders(<InputScreen />);
  for (const preset of presets.presets) {
    expect(screen.getByRole("heading", { name: preset.title })).toBeVisible();
  }
  const target = screen.getByLabelText("Target use");
  expect(Array.from(target.querySelectorAll("option")).map((option) => option.textContent)).toEqual([
    "Choose…",
    "Protein Isolate",
    "Protein Rich Flour",
    "Protein Concentrate",
  ]);
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
