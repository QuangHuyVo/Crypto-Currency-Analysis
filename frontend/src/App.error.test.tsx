import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "./App";

describe("App API errors", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 503,
        statusText: "Service Unavailable",
        text: async () => "rate limited",
      })),
    );
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it("shows a visible error when history request fails", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(/rate limited|503/i);
    });
  });
});
