import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "@/test/render";

import { Num } from "./Num";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.reject(new Error("offline"))),
  );
});

describe("<Num/>", () => {
  it("formats rupees with Indian digit grouping and always shows a tag chip", () => {
    renderWithProviders(
      <Num
        v={{
          value: 100000,
          unit: "INR/kg protein",
          tag: "published",
          grade: "C",
          source_ids: [],
          alpha: null,
        }}
      />,
    );
    expect(screen.getByText("₹1,00,000")).toBeInTheDocument();
    expect(screen.getByTitle("published")).toBeInTheDocument();
    expect(screen.getAllByText("published").length).toBeGreaterThan(0);
  });

  it("shows the P10–P90 range for ranges and the transferred badge when alpha < 0.7", () => {
    renderWithProviders(
      <Num
        v={{
          p10: 0.4,
          p50: 0.5,
          p90: 0.6,
          unit: "fraction",
          tag: "assumed",
          grade: "D",
          source_ids: [],
          alpha: 0.4,
        }}
      />,
    );
    expect(screen.getByText("50%")).toBeInTheDocument();
    expect(screen.getByText("40%–60%")).toBeInTheDocument();
    expect(screen.getByText("transferred")).toBeInTheDocument();
  });

  it("opens the details on activation and closes with Escape", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <Num
        v={{
          value: 0.53,
          unit: "probability",
          tag: "published",
          grade: "B",
          source_ids: ["murugeswari_2023"],
          alpha: null,
        }}
      />,
    );
    await user.click(screen.getByTestId("num"));
    expect(screen.getByText("Evidence grade")).toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByText("Evidence grade")).not.toBeInTheDocument();
  });
});
