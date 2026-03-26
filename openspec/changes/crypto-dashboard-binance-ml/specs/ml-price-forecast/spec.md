## ADDED Requirements

### Requirement: Build training features from OHLCV

The system SHALL derive a fixed feature set from historical candles (e.g., lagged returns, rolling statistics) aligned to the chosen bar interval, suitable for supervised learning.

#### Scenario: Feature matrix construction

- **WHEN** a minimum number of historical bars is available for the symbol and interval
- **THEN** the system produces a feature matrix and target vector with rows aligned to valid timestamps and no lookahead leakage from future bars

#### Scenario: Insufficient history

- **WHEN** available history is below the minimum required for feature computation
- **THEN** the system refuses training and returns an explicit “insufficient data” outcome

### Requirement: Train and evaluate a baseline model

The system SHALL train a versioned baseline model on a time-based train/validation split, record key metrics (e.g., MAE or direction accuracy), and save artifacts (model file + metadata) to a defined location.

#### Scenario: Successful training run

- **WHEN** training completes on valid input data
- **THEN** the system persists the model artifact, schema/version of features, metrics on validation, and training time range

#### Scenario: Failed training

- **WHEN** training fails due to numerical issues or empty splits
- **THEN** the system aborts without overwriting the last known-good model and reports the failure reason

### Requirement: Serve predictions for the active context

The system SHALL expose an API or callable interface that returns a prediction for the latest feature row built from the most recent candles, including timestamp of the last bar used.

#### Scenario: Inference with loaded model

- **WHEN** a trained model is present and current features can be built
- **THEN** the system returns a prediction value or class, the bar timestamp, and model version identifier

#### Scenario: No model available

- **WHEN** no model artifact exists or features cannot be built
- **THEN** the system returns a structured “unavailable” response without fabricating values

### Requirement: Disclose limitations

The system SHALL label prediction output as non-advisory experimental output and SHALL NOT present predictions as guaranteed or profit-making guidance.

#### Scenario: API or UI presentation

- **WHEN** predictions are shown to a user
- **THEN** accompanying text or fields indicate experimental ML output, not financial advice
