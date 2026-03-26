## 1. Backend: as-of prediction API

- [x] 1.1 Extend prediction endpoint to accept optional `as_of` (ISO-8601 UTC bar open); document behavior when omitted (latest bar unchanged).
- [x] 1.2 Validate `as_of` is on-interval for the requested symbol/interval; return structured 4xx when out of range, misaligned, or interval is below 4h policy for as-of mode.
- [x] 1.3 Truncate candle input to the feature builder so no bar after the as-of bar contributes; verify no lookahead in unit tests.
- [x] 1.4 Return canonical bar timestamp used, model version, and prediction payload shape consistent with existing clients when `as_of` is present.
- [x] 1.5 Add API tests: latest-only (no regression), valid as_of, insufficient history, invalid grid, unsupported short interval.

## 2. Frontend: crosshair click and gating

- [x] 2.1 Define supported-interval set (4h, 1d, 1w, 1M) shared or mirrored with backend policy.
- [x] 2.2 On chart click, resolve lightweight-charts crosshair logical time to containing candle open time; skip or show message when interval unsupported.
- [x] 2.3 Debounce or guard duplicate rapid clicks; trigger prediction fetch with `as_of` after anchor resolution.
- [x] 2.4 For forming bar, pass open time per design and show “current bar as of last update” copy where appropriate.

## 3. Dashboard prediction panel

- [x] 3.1 Display labeled as-of bar time when the last successful request used `as_of`; fall back to latest-bar label when not.
- [x] 3.2 Preserve experimental / non-advisory disclaimer and model version fields from existing panel.
- [x] 3.3 Handle API errors (invalid as_of, insufficient data) without showing stale prediction numbers.

## 4. Verification

- [x] 4.1 Run backend test suite; add or update frontend tests if the project covers prediction/chart flows.
- [x] 4.2 Manual smoke: 4h chart, click a past bar, confirm panel timestamp and value change; switch to 1h and confirm as-of flow is blocked with explanatory UI.
