## ADDED Requirements

### Requirement: Fetch historical OHLCV from Binance

The system SHALL retrieve candlestick (OHLCV) data for a configured symbol and interval from Binance public REST endpoints and normalize timestamps to UTC.

#### Scenario: Successful klines fetch

- **WHEN** a valid symbol and interval are requested and Binance returns data
- **THEN** the system returns a chronological series of candles with open, high, low, close, and volume fields

#### Scenario: Invalid symbol

- **WHEN** Binance responds with an error for an unknown or unsupported symbol
- **THEN** the system surfaces a clear error to the caller and does not return partial data as success

### Requirement: Stream live market updates

The system SHALL maintain a live connection (WebSocket) or a rate-safe polling loop to receive current price or kline updates for the active symbol and push updates to downstream consumers.

#### Scenario: Connection loss

- **WHEN** the live feed disconnects or errors
- **THEN** the system attempts reconnection with backoff and logs the incident without crashing the process

#### Scenario: Rate limit approached

- **WHEN** outbound request frequency nears documented Binance limits
- **THEN** the system throttles or batches requests and preserves stability over lowest latency

### Requirement: Cache recent candles

The system SHALL persist or cache recent OHLCV data locally so that restarts and dashboard loads do not require a full history refetch beyond the configured lookback window.

#### Scenario: Cache hit on dashboard load

- **WHEN** the dashboard requests recent history and cached data covers the requested window
- **THEN** the system serves from cache and optionally reconciles the latest closed candle with REST
