## MODIFIED Requirements

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
