"""24h volume ranking for USDT pairs."""

from app.binance.ticker_24hr import top_usdt_pairs_by_quote_volume


def test_top_by_quote_volume_orders_and_caps():
    symbols = ["ZZ/USDT", "BTC/USDT", "ETH/USDT"]
    tickers = [
        {"symbol": "ETHUSDT", "quoteVolume": "100"},
        {"symbol": "BTCUSDT", "quoteVolume": "999"},
        {"symbol": "ZZUSDT", "quoteVolume": "50"},
        {"symbol": "DOGEUSDT", "quoteVolume": "99999"},
    ]
    out = top_usdt_pairs_by_quote_volume(symbols, tickers, limit=2)
    assert out == ["BTC/USDT", "ETH/USDT"]


def test_top_skips_invalid_ticker_rows():
    symbols = ["BTC/USDT"]
    tickers = [
        {"symbol": "BTCUSDT", "quoteVolume": "not-a-float"},
        {"symbol": "BTCUSDT", "quoteVolume": "10"},
    ]
    out = top_usdt_pairs_by_quote_volume(symbols, tickers, limit=10)
    assert out == ["BTC/USDT"]
