import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, expect, it, vi } from "vitest";
import { type PropsWithChildren } from "react";
import { api, type AnalyzeResponse } from "./client";
import { useAnalysis } from "./hooks";
import { useStore } from "@/store";
import "@/i18n";

afterEach(() => {
  vi.restoreAllMocks();
  useStore.setState({ request: null, runRevision: 0, presetId: null, screen: "input" });
});

it("withholds the old case throughout a new request's debounce and network response", async () => {
  let finish: ((result: { data: AnalyzeResponse; offline: boolean }) => void) | undefined;
  vi.spyOn(api, "analyze")
    .mockResolvedValueOnce({ data: { case_id: "CASE-ONE" } as AnalyzeResponse, offline: false })
    .mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
  useStore
    .getState()
    .runRequest({ byproduct: "sunflower_cake", application: "extruded_snack" }, "sunflower_snack");
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const wrapper = ({ children }: PropsWithChildren) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  const { result, unmount } = renderHook(() => useAnalysis(), { wrapper });
  await waitFor(() => expect(result.current.data?.data.case_id).toBe("CASE-ONE"));
  act(() =>
    useStore
      .getState()
      .runRequest({ byproduct: "pea_protein_isolate", application: "beverage" }, "pea_beverage"),
  );
  expect(result.current.data).toBeUndefined();
  await waitFor(() => expect(api.analyze).toHaveBeenCalledTimes(2));
  expect(result.current.data).toBeUndefined();
  await act(async () => finish!({ data: { case_id: "CASE-TWO" } as AnalyzeResponse, offline: false }));
  await waitFor(() => expect(result.current.data?.data.case_id).toBe("CASE-TWO"));
  unmount();
  client.clear();
});
