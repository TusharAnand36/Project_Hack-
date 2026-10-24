import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { expect, it, vi } from "vitest";

import Site from "./Site";

vi.mock("./App", () => ({ default: () => <h1>Decision workspace</h1> }));

it("opens the public pages, keeps navigation accessible, and launches the decision workspace", () => {
  const scroll = vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  window.location.hash = "#/";
  const { unmount } = render(<Site />);
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("A second life.");
  const menu = screen.getByRole("button", { name: "Open navigation" });
  fireEvent.click(menu);
  expect(menu).toHaveAttribute("aria-expanded", "true");

  const navigate = (hash: string) =>
    act(() => {
      window.location.hash = hash;
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
  navigate("#/about");
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Curious about food.");
  expect(
    within(screen.getByRole("navigation", { name: "Main navigation" })).getByRole("link", {
      name: "About us",
    }),
  ).toHaveAttribute("aria-current", "page");
  expect(menu).toHaveAttribute("aria-expanded", "false");
  navigate("#/mission");
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Keep the value.");
  navigate("#/how-it-works");
  expect(screen.getByRole("heading", { name: "Decision memo" })).toBeInTheDocument();
  expect(screen.getByText("Do I need my own lab results to try it?")).toBeInTheDocument();
  expect(screen.getAllByRole("link", { name: "Open Compass" })[0]).toHaveAttribute("href", "#/compass");
  navigate("#/compass");
  expect(screen.getByRole("heading", { name: "Decision workspace" })).toBeInTheDocument();
  navigate("#/unknown");
  expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("A second life.");
  expect(document.activeElement).toBe(screen.getByRole("main"));
  unmount();
  scroll.mockRestore();
});
