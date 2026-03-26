import { useEffect, useRef } from "react";
import {
  ColorType,
  createChart,
  CrosshairMode,
  type CandlestickData,
  type HistogramData,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
} from "lightweight-charts";

export type CandleBar = {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type CrosshairOHLC = {
  timeLabel: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
};

export type ChartType = "candle" | "line";

type Props = {
  candles: CandleBar[];
  interval: string;
  chartType: ChartType;
  /** Increments when symbol, interval, or chart type changes — triggers fitContent; polling must not bump this. */
  viewRevision: number;
  onCrosshair: (p: CrosshairOHLC | null) => void;
};

function buildCandleData(bars: CandleBar[]): CandlestickData[] {
  return bars.map((c) => ({
    time: Math.floor(c.time / 1000) as UTCTimestamp,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  }));
}

function buildLineData(bars: CandleBar[]): LineData[] {
  return bars.map((c) => ({
    time: Math.floor(c.time / 1000) as UTCTimestamp,
    value: c.close,
  }));
}

function buildVolumeData(bars: CandleBar[]): HistogramData[] {
  return bars.map((c) => ({
    time: Math.floor(c.time / 1000) as UTCTimestamp,
    value: c.volume,
    color: c.close >= c.open ? "rgba(38, 166, 154, 0.45)" : "rgba(239, 83, 80, 0.45)",
  }));
}

export function CandleVolumeChart({ candles, interval, chartType, viewRevision, onCrosshair }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const priceSeriesRef = useRef<ISeriesApi<"Candlestick"> | ISeriesApi<"Line"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const lastFittedViewRevision = useRef<number>(-1);
  const candlesRef = useRef(candles);
  candlesRef.current = candles;
  const cbRef = useRef(onCrosshair);
  cbRef.current = onCrosshair;

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;

    const chart = createChart(el, {
      layout: {
        background: { type: ColorType.Solid, color: "#0a0a0a" },
        textColor: "#b3b3b3",
      },
      grid: {
        vertLines: { color: "#1f1f1f" },
        horzLines: { color: "#1f1f1f" },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: "#333333" },
      timeScale: {
        borderColor: "#333333",
        timeVisible: true,
        secondsVisible: interval === "1m",
      },
    });

    const priceSeries =
      chartType === "line"
        ? chart.addLineSeries({
            color: "#58a6ff",
            lineWidth: 2,
          })
        : chart.addCandlestickSeries({
            upColor: "#26a69a",
            downColor: "#ef5350",
            borderVisible: false,
            wickUpColor: "#26a69a",
            wickDownColor: "#ef5350",
          });

    const volumeSeries = chart.addHistogramSeries({
      color: "#26a69a",
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.78, bottom: 0 },
    });
    priceSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.05, bottom: 0.2 },
    });

    priceSeriesRef.current = priceSeries;
    volumeSeriesRef.current = volumeSeries;
    chartRef.current = chart;

    if (chartType === "line") {
      (priceSeries as ISeriesApi<"Line">).setData(buildLineData(candlesRef.current));
    } else {
      (priceSeries as ISeriesApi<"Candlestick">).setData(buildCandleData(candlesRef.current));
    }
    volumeSeries.setData(buildVolumeData(candlesRef.current));

    chart.subscribeCrosshairMove((param) => {
      if (!param.point || param.point.x < 0 || param.point.y < 0) {
        cbRef.current(null);
        return;
      }
      const vdata = param.seriesData.get(volumeSeries) as HistogramData | undefined;
      const t = param.time;
      let timeLabel: string;
      if (typeof t === "number") {
        timeLabel = new Date(t * 1000).toISOString();
      } else {
        timeLabel = String(t);
      }

      if (chartType === "line") {
        const ts = typeof param.time === "number" ? param.time : null;
        const bar =
          ts != null
            ? candlesRef.current.find((b) => Math.floor(b.time / 1000) === ts)
            : undefined;
        const vol = vdata && typeof vdata.value === "number" ? vdata.value : null;
        if (bar) {
          cbRef.current({
            timeLabel,
            open: bar.open,
            high: bar.high,
            low: bar.low,
            close: bar.close,
            volume: vol,
          });
          return;
        }
        const ld = param.seriesData.get(priceSeries) as LineData | undefined;
        if (ld && typeof ld.value === "number") {
          cbRef.current({
            timeLabel,
            open: ld.value,
            high: ld.value,
            low: ld.value,
            close: ld.value,
            volume: vol,
          });
        } else {
          cbRef.current(null);
        }
        return;
      }

      const cdata = param.seriesData.get(priceSeries) as CandlestickData | undefined;
      if (!cdata || cdata.open === undefined) {
        cbRef.current(null);
        return;
      }
      cbRef.current({
        timeLabel,
        open: cdata.open,
        high: cdata.high,
        low: cdata.low,
        close: cdata.close,
        volume: vdata && typeof vdata.value === "number" ? vdata.value : null,
      });
    });

    const ro = new ResizeObserver(() => {
      const r = el.getBoundingClientRect();
      const w = Math.max(2, Math.floor(r.width));
      const h = Math.max(2, Math.floor(r.height));
      chart.resize(w, h);
    });
    ro.observe(el);
    queueMicrotask(() => {
      const r = el.getBoundingClientRect();
      chart.resize(Math.max(2, Math.floor(r.width)), Math.max(2, Math.floor(r.height)));
    });

    return () => {
      ro.disconnect();
      chart.remove();
      lastFittedViewRevision.current = -1;
      chartRef.current = null;
      priceSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, [interval, chartType]);

  useEffect(() => {
    const p = priceSeriesRef.current;
    const v = volumeSeriesRef.current;
    const ch = chartRef.current;
    if (!p || !v || !ch) return;
    v.setData(buildVolumeData(candles));
    if (chartType === "line") {
      (p as ISeriesApi<"Line">).setData(buildLineData(candles));
    } else {
      (p as ISeriesApi<"Candlestick">).setData(buildCandleData(candles));
    }
    if (viewRevision > lastFittedViewRevision.current) {
      ch.timeScale().fitContent();
      lastFittedViewRevision.current = viewRevision;
    }
  }, [candles, chartType, viewRevision]);

  return <div ref={wrapRef} style={{ width: "100%", height: "100%", minHeight: 0 }} />;
}
