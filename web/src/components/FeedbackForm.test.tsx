import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";
import snapshot from "../../public/snapshots/pea_beverage.en.json";
import { api, type AnalyzeResponse } from "@/api/client";
import { renderWithProviders } from "@/test/render";
import { FeedbackForm } from "./FeedbackForm";

afterEach(() => vi.restoreAllMocks());
const data = { ...snapshot, case_id: "00000000-0000-0000-0000-000000000001" } as unknown as AnalyzeResponse;

it("submits feedback for the exact case and confirms only a successful database receipt", async () => {
  const save = vi
    .spyOn(api, "feedback")
    .mockResolvedValue({ saved: true, case_id: data.case_id!, context: data.feedback_context });
  renderWithProviders(<FeedbackForm data={data} disabled={false} />);
  await userEvent.selectOptions(screen.getByLabelText("Main issue to investigate"), "texture");
  await userEvent.type(
    screen.getByLabelText("Private case notes (optional)"),
    "Trial needs texture validation",
  );
  await userEvent.click(screen.getByRole("button", { name: "Save case feedback" }));
  expect(await screen.findByText(/Feedback saved to this case/)).toBeInTheDocument();
  expect(save).toHaveBeenCalledWith(
    expect.objectContaining({ case_id: data.case_id, issue: "texture", outcome: "not_tested" }),
  );
});

it("does not pretend that an offline snapshot can save feedback", () => {
  const save = vi.spyOn(api, "feedback");
  renderWithProviders(<FeedbackForm data={{ ...data, case_id: null }} disabled />);
  expect(screen.getByText(/Offline snapshots do not create or save/)).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: "Save case feedback" })).not.toBeInTheDocument();
  expect(save).not.toHaveBeenCalled();
});

it("keeps errors visible and never claims an unsuccessful save", async () => {
  vi.spyOn(api, "feedback").mockRejectedValue(new Error("Database unavailable; feedback not saved"));
  renderWithProviders(<FeedbackForm data={data} disabled={false} />);
  await userEvent.click(screen.getByRole("button", { name: "Save case feedback" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("feedback not saved");
  expect(screen.queryByText(/Feedback saved to this case/)).not.toBeInTheDocument();
});
