import { screen, within } from "@testing-library/react";
import { expect, it } from "vitest";
import snapshot from "../../public/snapshots/sunflower_snack.en.json";
import type { AnalyzeResponse } from "@/api/client";
import { renderWithProviders } from "@/test/render";
import { FunctionalComparison } from "./FunctionalComparison";

it("separates flour, extracted isolate and pea-study conditions without inventing comparable results", () => {
  renderWithProviders(<FunctionalComparison data={snapshot as unknown as AnalyzeResponse} />);
  expect(screen.getByRole("columnheader", { name: "Whole-cake flour reference" })).toBeInTheDocument();
  expect(
    screen.getByRole("columnheader", { name: "Extracted oilseed isolate reference" }),
  ).toBeInTheDocument();
  const row = screen.getByText("Water absorption capacity").closest("tr")!;
  expect(within(row).getByText(/2.8.*4.2/)).toBeInTheDocument();
  expect(within(row).getByText(/3.2.*4.5/)).toBeInTheDocument();
  expect(within(row).getByText(/Not reported in the supplied study/)).toBeInTheDocument();
  expect(screen.getByText(/^These studies do not establish a head-to-head winner/)).toBeInTheDocument();
  expect(screen.getAllByRole("row")).toHaveLength(9);
});
