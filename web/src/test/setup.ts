import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

import "@/i18n";

afterEach(() => cleanup());

// jsdom has no ResizeObserver (Radix popover positioning uses it)
globalThis.ResizeObserver ??= class {
  observe() {}
  unobserve() {}
  disconnect() {}
};
