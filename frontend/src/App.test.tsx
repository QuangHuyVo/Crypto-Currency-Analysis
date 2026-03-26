import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";

function installFetchMock() {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const u = typeof input === "string" ? input : input.toString();
      if (u.includes("/market/symbols")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ symbols: ["BTC/USDT"], top_by_volume: ["BTC/USDT"] }),
        } as Response);
      }
      if (u.includes("/market/history")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            symbol: "BTC/USDT",
            interval: "1m",
            candles: [
              {
                time: 1_700_000_000_000,
                open: 1,
                high: 2,
                low: 0.5,
                close: 1.5,
                volume: 100,
              },
            ],
          }),
        } as Response);
      }
      if (u.includes("/predict")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            available: false,
            reason: "none",
            disclaimer: "Not advice",
          }),
        } as Response);
      }
      return Promise.resolve({ ok: false, status: 404, text: async () => "" } as Response);
    }),
  );
}

describe("App", () => {
  beforeEach(() => {
    installFetchMock();
  });

  it("shows dashboard title", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { name: /crypto trading/i })).toBeInTheDocument();
  });

  it("shows timeframe buttons including 1m and 1d", async () => {
    render(<App />);
    expect(await screen.findByRole("button", { name: "1m" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "1d" })).toBeInTheDocument();
  });
});
