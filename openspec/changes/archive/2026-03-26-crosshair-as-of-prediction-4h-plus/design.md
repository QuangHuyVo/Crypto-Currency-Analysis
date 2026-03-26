## Context

The product already serves ML price predictions built from the latest candles and shows them in a dashboard panel. Lightweight Charts provides a crosshair; users reason about **historical** bars, so “latest bar only” is limiting. The proposal anchors inference to **the OHLC bar under the crosshair at user click**, gated to **4h, 1d, 1w, 1M** (and equivalent long intervals if added later).

Constraints: training/feature schemas assume interval-aligned timestamps; **no lookahead** beyond the chosen bar’s close; public disclaimer that output is experimental, not advice.

## Goals / Non-Goals

**Goals:**

- Let the user request a prediction **as of** a specific selected bar using a single clear gesture (crosshair position + click).
- Pass a stable **as-of** key (see decisions) from UI → API; backend truncates candle history so the feature row matches that bar.
- Enforce the **4h+** policy in both UI and API.
- Preserve a backward-compatible default: if `as_of` is omitted, behavior remains **latest bar** (same as today).

**Non-Goals:**

- Predictions on **< 4h** intervals for this flow.
- Retraining models per as-of bar; only **inference** path changes.
- Pattern detection, drawings, or multi-horizon forecast ensembles.

## Decisions

1. **As-of identity: bar open time (UTC)**  
   **Rationale**: Candle series are keyed by open time in most exchange/API models; unambiguous per `(symbol, interval)`.  
   **Alternatives**: Close time (harder to align with “bar under cursor” in some libs); index offset (fragile across pagination).

2. **“Bar under crosshair at click”**  
   On pointer down/up on the plot, resolve the crosshair’s logical time to the **containing** candle for the active interval (same bar the crosshair tooltip uses). That candle’s **open time** is `as_of`.  
   **Alternatives**: Nearest bar (ambiguous at boundaries); last **closed** bar only (rejects user choice (2)).

3. **Forming (in-progress) bar**  
   Allow selection of the **current** incomplete bar if the user clicks it: features use only data **through the last available update** for that bar (still no future bars). Document in UI that the anchor is “current bar as of last update.”  
   **Alternatives**: Disable clicks on forming bar (simpler but inconsistent with “bar under crosshair”).

4. **API shape**  
   Extend existing prediction GET/POST with optional `as_of` (ISO-8601 UTC instant matching bar open). Validation: must be on-interval for the requested `interval`; must not be after the latest available bar open by more than one bar length (tolerance configurable); reject **< 4h** intervals when `as_of` mode is used, or reject entire request for unsupported interval.  
   **Alternatives**: Separate `/predict/as-of` endpoint (more surface area).

5. **Feature builder**  
   Reuse existing feature pipeline: filter candles to include the as-of bar and all prior rows needed for lags/windows; compute the row for the as-of timestamp only.  
   **Alternatives**: Client sends precomputed features (rejected: leaks schema, harms consistency).

6. **UI**  
   Prediction CTA or automatic fetch on chart click after crosshair settled (debounce rapid clicks). Panel shows **As-of:** open time formatted to interval, plus existing model version and disclaimer. Sub-4h: hide anchor affordance or show “Supported on 4h+ intervals.”

## Risks / Trade-offs

- **[Risk] Timezone / DST display confusion** → Show UTC or explicit offset in tooltip/panel; store/transmit UTC only.  
- **[Risk] Off-grid `as_of` from floating-point time** → Snap to interval grid server-side; return 400 with clear message.  
- **[Risk] Sparse history at early bars** → Same “insufficient data” behavior as training spec; surface in UI.  
- **[Trade-off] Default remains “latest” when `as_of` omitted** → Simpler migration; document that explicit click path is for historical what-if.

## Migration Plan

1. Ship backend: accept optional `as_of`, validate interval, truncate features.  
2. Ship frontend: wire click → `as_of`, interval gate, panel labels.  
3. No DB migration if candles already keyed by open time.  
4. **Rollback**: feature flag or revert commit; omitting `as_of` keeps prior behavior.

## Open Questions

- Exact debouncing vs explicit “Predict at crosshair” button (product preference).  
- Whether to show both “latest” and “as-of” predictions side-by-side (initially: single panel reflecting last action).
