## MODIFIED Requirements

### Requirement: Serve predictions for the active context

The system SHALL expose an API or callable interface that returns a prediction for a feature row aligned to either (a) the **latest** available bar when `as_of` is omitted, or (b) the bar whose **open time** equals `as_of` when provided. The response SHALL include the bar timestamp used for the feature row (last bar included in the feature vector), the model version identifier, and SHALL build features using only candles with timestamps **not after** that bar’s close-equivalent window—no data from later bars.

#### Scenario: Inference with loaded model and latest bar

- **WHEN** a trained model is present, `as_of` is omitted, and current features can be built for the latest bar
- **THEN** the system returns a prediction value or class, the latest bar timestamp used, and model version identifier

#### Scenario: Inference with loaded model and explicit as_of

- **WHEN** a trained model is present, `as_of` is provided and valid for the symbol and interval, and sufficient prior history exists to build features for that bar without lookahead
- **THEN** the system returns a prediction value or class, the `as_of` bar timestamp (or equivalent canonical bar key), and model version identifier

#### Scenario: No model available

- **WHEN** no model artifact exists or features cannot be built
- **THEN** the system returns a structured “unavailable” response without fabricating values

#### Scenario: Invalid or unsupported as_of

- **WHEN** `as_of` is not aligned to the requested interval, is outside available history, or the interval is excluded from as-of prediction policy
- **THEN** the system returns a structured error without fabricating a prediction
