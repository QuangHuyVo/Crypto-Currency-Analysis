## ADDED Requirements

### Requirement: Select symbol and timeframe

The user SHALL be able to choose a trading pair (symbol) and candle interval from the dashboard; the selection SHALL drive data and prediction requests.

#### Scenario: Change symbol

- **WHEN** the user selects a different symbol from supported options
- **THEN** the dashboard requests the corresponding market data and updates charts without requiring a full page reload

#### Scenario: Change interval

- **WHEN** the user selects a different interval
- **THEN** the dashboard reloads the candle series for that interval and refreshes the prediction panel state

### Requirement: Display live or near-live price chart

The dashboard SHALL render an interactive price (or candlestick) chart for the active symbol and interval, updating as new data arrives from the backend.

#### Scenario: Data loading

- **WHEN** data is being fetched
- **THEN** the dashboard shows a loading state

#### Scenario: Stream or poll updates

- **WHEN** new candles or ticker updates are received
- **THEN** the chart updates to reflect the latest values within the UI refresh mechanism

### Requirement: Show prediction panel

The dashboard SHALL display model output (when available), model version, and timestamp of the bar used for the feature row—either the **latest** bar when no anchor was chosen, or the **as-of** bar open time when the user invoked crosshair-click prediction—alongside a short limitation notice.

#### Scenario: Prediction available for latest bar

- **WHEN** the prediction API returns a successful payload without an explicit user-chosen `as_of`
- **THEN** the dashboard shows the prediction fields, the last bar timestamp, model version, and the limitation notice

#### Scenario: Prediction available for anchored bar

- **WHEN** the prediction API returns a successful payload for a request that included `as_of` from the crosshair-click flow
- **THEN** the dashboard shows the prediction fields, the as-of bar timestamp clearly labeled, model version, and the limitation notice

#### Scenario: Prediction unavailable

- **WHEN** the prediction API indicates no model or insufficient data
- **THEN** the dashboard shows a clear empty or error state without stale numbers

### Requirement: Surface errors from the backend

The dashboard SHALL display user-visible errors when market data or prediction requests fail (network, rate limit, provider error).

#### Scenario: Backend error

- **WHEN** an API call returns a non-success status or times out
- **THEN** the dashboard shows an error message and retains or clears charts according to a defined safe behavior (e.g., keep last good data with a stale badge)
