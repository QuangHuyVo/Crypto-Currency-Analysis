import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { apiGet } from "./client";

describe("apiGet", () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    vi.stubEnv("VITE_API_BASE", "/api");
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.unstubAllEnvs();
  });

  it("GETs JSON from API base + path", async () => {
    const urls: string[] = [];
    globalThis.fetch = vi.fn((input: RequestInfo | URL) => {
      urls.push(String(input));
      return Promise.resolve(
        new Response(JSON.stringify({ hello: 1 }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );
    }) as typeof fetch;

    const data = await apiGet<{ hello: number }>("health");
    expect(data).toEqual({ hello: 1 });
    expect(urls[0]).toMatch(/\/api\/health$/);
  });
});
