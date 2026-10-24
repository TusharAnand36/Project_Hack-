import { beforeEach, expect, it } from "vitest";
import { useStore } from "./store";

beforeEach(() => useStore.setState({ request: null, presetId: null }));

it("carries shared pea settings across materials without using an incompatible snapshot", () => {
  useStore
    .getState()
    .runRequest({ byproduct: "groundnut_cake", application: "beverage" }, "groundnut_beverage");
  expect(useStore.getState().presetId).toBe("groundnut_beverage");
  useStore.getState().patchRequest((r) => ({ ...r, pea: { base_usd_per_kg: 4 } }));
  useStore
    .getState()
    .runRequest({ byproduct: "pea_protein_isolate", application: "beverage" }, "pea_beverage");
  expect(useStore.getState().request?.pea?.base_usd_per_kg).toBe(4);
  expect(useStore.getState().presetId).toBeNull();
});
