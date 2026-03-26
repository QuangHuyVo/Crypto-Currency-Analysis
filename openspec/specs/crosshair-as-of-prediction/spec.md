## ADDED Requirements

### Requirement: Resolve as-of bar from crosshair click

When the user activates a chart click-to-predict gesture, the client SHALL resolve the pointer event to the **single OHLC bar** that contains the crosshair time for the **active** interval, and SHALL use that bar’s **open time** (UTC) as `as_of`.

#### Scenario: Click on historical bar

- **WHEN** the user clicks the chart while the crosshair is over a fully closed bar on a supported interval
- **THEN** the client sends a prediction request including `as_of` equal to that bar’s open time

#### Scenario: Click on forming bar

- **WHEN** the user clicks the chart while the crosshair is over the current in-progress bar
- **THEN** the client sends `as_of` for that bar’s open time and the UI indicates the anchor is the current bar as of the latest received update

### Requirement: Gate as-of prediction to long intervals

As-of prediction via crosshair click SHALL be available only when the active interval is one of **4h, 1d, 1w, 1M**, or another interval explicitly classified as long-horizon in product configuration. Shorter intervals SHALL not trigger as-of prediction requests.

#### Scenario: Supported interval

- **WHEN** the active interval is 4h or larger per policy
- **THEN** the click-to-predict gesture is enabled and may call the prediction API with `as_of`

#### Scenario: Unsupported interval

- **WHEN** the active interval is below the 4h threshold
- **THEN** the UI does not send as-of prediction requests for crosshair clicks and SHALL show an explanatory state if the user attempts the gesture

### Requirement: Pass as-of to backend

The client SHALL include `as_of` as an ISO-8601 UTC timestamp representing bar open time in prediction API requests triggered by the crosshair-click flow.

#### Scenario: Successful request shape

- **WHEN** the user has clicked to anchor a bar and the client issues the prediction call
- **THEN** the request includes `symbol`, `interval`, and `as_of` fields expected by the server contract

### Requirement: Display anchor context

The dashboard SHALL show which bar the prediction was computed for (as-of open time, formatted for the active interval) alongside existing prediction fields and the experimental-output disclaimer.

#### Scenario: After anchored prediction

- **WHEN** a prediction response returns successfully for an `as_of` request
- **THEN** the prediction panel shows the as-of bar time and does not imply financial advice beyond existing ML limitations copy
