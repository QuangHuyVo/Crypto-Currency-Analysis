import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  CandleVolumeChart,
  type CandleBar,
  type ChartType,
  type CrosshairOHLC,
} from "./components/CandleVolumeChart";
import { SymbolSearch } from "./components/SymbolSearch";

const INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d", "1w", "1M"] as const;
type Interval = (typeof INTERVALS)[number];

function historyLimitForInterval(iv: Interval): number {
  switch (iv) {
    case "4h":
      return 500;
    case "1d":
      return 400;
    case "1w":
      return 100;
    case "1M":
      return 36;
    default:
      return 200;
  }
}

const FALLBACK_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"];

const theme = {
  pageBg: "#0a0a0a",
  panel: "#141414",
  border: "#262626",
  text: "#e5e5e5",
  muted: "#a3a3a3",
  accent: "#e50914",
};

type HistoryResponse = {
  symbol: string;
  interval: string;
  candles: {
    time: number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
};

type PredictResponse = {
  available: boolean;
  reason?: string;
  disclaimer: string;
  prediction_label?: string;
  model_version?: string;
  last_bar_time_ms?: number;
  detail?: string;
};

function readUrlState(): { symbol: string; interval: Interval } {
  const p = new URLSearchParams(window.location.search);
  const sym = p.get("symbol");
  const iv = p.get("interval") as Interval | null;
  return {
    symbol: sym && sym.length > 0 ? decodeURIComponent(sym) : "BTC/USDT",
    interval: iv && (INTERVALS as readonly string[]).includes(iv) ? iv : "1m",
  };
}

function writeUrlState(symbol: string, interval: string) {
  const u = new URL(window.location.href);
  u.searchParams.set("symbol", symbol);
  u.searchParams.set("interval", interval);
  window.history.replaceState(null, "", u);
}

function candlesToBars(candles: HistoryResponse["candles"]): CandleBar[] {
  return candles.map((c) => ({
    time: c.time,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
    volume: c.volume,
  }));
}

export default function App() {
  const initial = useMemo(() => readUrlState(), []);
  const [symbol, setSymbol] = useState(initial.symbol);
  const [interval, setInterval] = useState<Interval>(initial.interval);
  const [bars, setBars] = useState<CandleBar[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stale, setStale] = useState(false);
  const [pred, setPred] = useState<PredictResponse | null>(null);
  const [symbolsList, setSymbolsList] = useState<string[]>(FALLBACK_SYMBOLS);
  const [topByVolume, setTopByVolume] = useState<string[]>([]);
  const [chartType, setChartType] = useState<ChartType>("candle");
  const [viewRevision, setViewRevision] = useState(1);
  const viewKeyRef = useRef(`${initial.symbol}|${initial.interval}|candle`);
  const [ohlcLegend, setOhlcLegend] = useState<CrosshairOHLC | null>(null);

  const onCrosshair = useCallback((p: CrosshairOHLC | null) => {
    setOhlcLegend(p);
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch(new URL("/api/market/symbols", window.location.origin).toString());
        if (!res.ok) return;
        const data = (await res.json()) as { symbols: string[]; top_by_volume?: string[] };
        if (Array.isArray(data.symbols) && data.symbols.length > 0) {
          setSymbolsList(data.symbols);
        }
        if (Array.isArray(data.top_by_volume)) {
          setTopByVolume(data.top_by_volume);
        }
      } catch {
        /* keep fallback */
      }
    })();
  }, []);

  useEffect(() => {
    writeUrlState(symbol, interval);
  }, [symbol, interval]);

  useEffect(() => {
    const key = `${symbol}|${interval}|${chartType}`;
    if (key !== viewKeyRef.current) {
      viewKeyRef.current = key;
      setViewRevision((x) => x + 1);
    }
  }, [symbol, interval, chartType]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable) return;
      const n = e.key;
      if (n >= "1" && n <= "8") {
        e.preventDefault();
        const ix = parseInt(n, 10) - 1;
        if (INTERVALS[ix]) setInterval(INTERVALS[ix]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const u = new URL("/api/market/history", window.location.origin);
      u.searchParams.set("symbol", symbol);
      u.searchParams.set("interval", interval);
      u.searchParams.set("limit", String(historyLimitForInterval(interval)));
      const res = await fetch(u.toString());
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `${res.status} ${res.statusText}`);
      }
      const data = (await res.json()) as HistoryResponse;
      setBars(candlesToBars(data.candles));
      setStale(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setStale(true);
    } finally {
      setLoading(false);
    }
  }, [symbol, interval]);

  const loadPredict = useCallback(async () => {
    try {
      const u = new URL("/api/predict", window.location.origin);
      u.searchParams.set("symbol", symbol);
      u.searchParams.set("interval", interval);
      const res = await fetch(u.toString());
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `${res.status}`);
      }
      setPred((await res.json()) as PredictResponse);
    } catch (e) {
      setPred({
        available: false,
        reason: "request_failed",
        disclaimer:
          "Experimental ML output only; not financial advice. Past performance does not guarantee future results.",
        detail: e instanceof Error ? e.message : String(e),
      });
    }
  }, [symbol, interval]);

  useEffect(() => {
    void loadHistory();
    void loadPredict();
  }, [loadHistory, loadPredict]);

  useEffect(() => {
    const id = window.setInterval(() => {
      void loadHistory();
      void loadPredict();
    }, 10_000);
    return () => window.clearInterval(id);
  }, [loadHistory, loadPredict]);

  return (
    <div
      style={{
        height: "100vh",
        minHeight: 0,
        background: theme.pageBg,
        color: theme.text,
        display: "flex",
        flexDirection: "column",
        fontFamily: "system-ui, Segoe UI, Roboto, sans-serif",
        overflow: "hidden",
      }}
    >
      <header
        style={{
          flexShrink: 0,
          padding: "0.75rem 1rem",
          borderBottom: `1px solid ${theme.border}`,
          background: theme.panel,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <h1 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            Crypto <span style={{ color: theme.accent }}>Trading</span>
          </h1>
          <span style={{ color: theme.muted, fontSize: "0.8rem" }}>
            Binance · experimental ML — not trading advice · keys <strong>1–8</strong> = timeframe
          </span>
        </div>
      </header>

      <div
        style={{
          flexShrink: 0,
          borderBottom: `1px solid ${theme.border}`,
        }}
      >
        <div style={{ padding: "0.6rem 1rem 0.4rem", width: "100%", boxSizing: "border-box" }}>
          <SymbolSearch symbols={symbolsList} topSymbols={topByVolume} value={symbol} onChange={setSymbol} />
        </div>
        <div
          style={{
            padding: "0.4rem 1rem 0.6rem",
            display: "flex",
            flexWrap: "wrap",
            gap: "0.75rem",
            alignItems: "center",
            width: "100%",
            boxSizing: "border-box",
          }}
        >
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }} aria-label="Chart type">
            {(["candle", "line"] as const).map((ct) => (
              <button
                key={ct}
                type="button"
                onClick={() => setChartType(ct)}
                style={{
                  padding: "0.35rem 0.65rem",
                  borderRadius: 4,
                  border: `1px solid ${chartType === ct ? theme.accent : theme.border}`,
                  background: chartType === ct ? "rgba(229, 9, 20, 0.2)" : theme.panel,
                  color: chartType === ct ? theme.text : theme.muted,
                  cursor: "pointer",
                  fontWeight: chartType === ct ? 600 : 400,
                  fontSize: "0.85rem",
                  textTransform: "capitalize",
                }}
              >
                {ct === "candle" ? "Candles" : "Line"}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }} aria-label="Timeframe">
            {INTERVALS.map((iv) => (
              <button
                key={iv}
                type="button"
                onClick={() => setInterval(iv)}
                style={{
                  padding: "0.35rem 0.65rem",
                  borderRadius: 4,
                  border: `1px solid ${iv === interval ? theme.accent : theme.border}`,
                  background: iv === interval ? "rgba(229, 9, 20, 0.2)" : theme.panel,
                  color: iv === interval ? theme.text : theme.muted,
                  cursor: "pointer",
                  fontWeight: iv === interval ? 600 : 400,
                  fontSize: "0.85rem",
                }}
              >
                {iv}
              </button>
            ))}
          </div>

          {ohlcLegend && (
            <div
              style={{
                marginLeft: "auto",
                fontSize: "0.78rem",
                color: theme.muted,
                fontVariantNumeric: "tabular-nums",
                display: "flex",
                flexWrap: "wrap",
                gap: "0.65rem",
              }}
            >
              <span title="Crosshair time">{ohlcLegend.timeLabel}</span>
              <span>O {ohlcLegend.open}</span>
              <span>H {ohlcLegend.high}</span>
              <span>L {ohlcLegend.low}</span>
              <span>C {ohlcLegend.close}</span>
              {ohlcLegend.volume != null && <span>V {ohlcLegend.volume}</span>}
            </div>
          )}

          {stale && (
            <span
              style={{ color: "#fbbf24", fontSize: "0.8rem", marginLeft: ohlcLegend ? 0 : "auto" }}
              title="Last request failed; data may be stale"
            >
              Stale / error
            </span>
          )}
        </div>
      </div>

      <div style={{ flex: 1, minHeight: 0, position: "relative" }}>
        {loading && bars.length === 0 && (
          <p style={{ position: "absolute", left: 16, top: 12, margin: 0, color: theme.muted, zIndex: 1 }}>
            Loading chart…
          </p>
        )}
        {error && (
          <p role="alert" style={{ position: "absolute", left: 16, top: 12, margin: 0, color: "#f87171", zIndex: 1 }}>
            {error}
          </p>
        )}
        <CandleVolumeChart
          candles={bars}
          interval={interval}
          chartType={chartType}
          viewRevision={viewRevision}
          onCrosshair={onCrosshair}
        />
      </div>

      <footer
        style={{
          flexShrink: 0,
          maxHeight: "28vh",
          overflow: "auto",
          padding: "0.75rem 1rem",
          borderTop: `1px solid ${theme.border}`,
          background: theme.panel,
        }}
      >
        <h2 style={{ margin: "0 0 0.5rem", fontSize: "0.95rem", color: theme.text }}>Prediction</h2>
        {!pred && <p style={{ margin: 0, color: theme.muted }}>Loading prediction…</p>}
        {pred && pred.available && (
          <div style={{ fontSize: "0.88rem" }}>
            <p style={{ margin: "0.25rem 0" }}>
              <strong>Signal:</strong> {pred.prediction_label ?? "n/a"}
            </p>
            <p style={{ margin: "0.25rem 0" }}>
              <strong>Model version:</strong> {pred.model_version ?? "unknown"}
            </p>
            {pred.last_bar_time_ms != null && (
              <p style={{ margin: "0.25rem 0" }}>
                <strong>Last bar (UTC ms):</strong> {pred.last_bar_time_ms}
              </p>
            )}
            <p style={{ fontSize: "0.8rem", color: theme.muted, margin: "0.5rem 0 0" }}>{pred.disclaimer}</p>
          </div>
        )}
        {pred && !pred.available && (
          <div style={{ fontSize: "0.88rem" }}>
            <p style={{ margin: "0.25rem 0" }}>No prediction available ({pred.reason ?? "unknown"}).</p>
            {pred.detail && <p style={{ color: theme.muted, margin: "0.25rem 0" }}>{pred.detail}</p>}
            <p style={{ fontSize: "0.8rem", color: theme.muted, margin: "0.5rem 0 0" }}>{pred.disclaimer}</p>
          </div>
        )}
      </footer>
    </div>
  );
}
