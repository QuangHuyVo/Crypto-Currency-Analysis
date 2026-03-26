"""exchangeInfo parsing for USDT spot symbols."""

from app.binance.exchange_info import parse_exchange_info_symbols


def test_parse_exchange_info_filters_usdt_spot_trading():
    raw = {
        "symbols": [
            {
                "baseAsset": "BTC",
                "quoteAsset": "USDT",
                "status": "TRADING",
                "permissions": ["SPOT"],
            },
            {
                "baseAsset": "ETH",
                "quoteAsset": "BUSD",
                "status": "TRADING",
                "permissions": ["SPOT"],
            },
            {
                "baseAsset": "X",
                "quoteAsset": "USDT",
                "status": "BREAK",
                "permissions": ["SPOT"],
            },
            {
                "baseAsset": "BAD",
                "quoteAsset": "USDT",
                "status": "TRADING",
                "permissions": ["MARGIN"],
            },
        ]
    }
    assert parse_exchange_info_symbols(raw) == ["BTC/USDT"]
