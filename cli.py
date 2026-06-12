"""
CLI entry point for the Binance Futures Testnet Trading Bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.01 --price 95000
  python cli.py --symbol BTCUSDT --side BUY  --type STOP_MARKET --quantity 0.01 --stop-price 94000
"""

import argparse
import sys

from bot.client import BinanceFuturesClient, BinanceAPIError
from bot.logging_config import setup_logging, get_logger
from bot.orders import place_order
from bot.validators import validate_order_params

import requests

# Initialise logging before anything else
setup_logging()
logger = get_logger("cli")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on the Binance USDT-M Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.01 --price 95000
  python cli.py --symbol BTCUSDT --side BUY  --type STOP_MARKET --quantity 0.01 --stop-price 94000
        """,
    )
    parser.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True,  help="BUY or SELL")
    parser.add_argument("--type",       required=True,  dest="order_type", help="MARKET or LIMIT")
    parser.add_argument("--quantity",   required=True,  type=float, help="Order quantity, e.g. 0.01")
    parser.add_argument("--price",      required=False, type=float, default=None, help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", required=False, type=float, default=None, dest="stop_price", help="Stop trigger price (required for STOP_MARKET orders)")
    return parser


def print_request_summary(symbol, side, order_type, quantity, price, stop_price):
    print("\n" + "=" * 55)
    print("         ORDER REQUEST SUMMARY")
    print("=" * 55)
    print(f"  Symbol     : {symbol.upper()}")
    print(f"  Side       : {side.upper()}")
    print(f"  Type       : {order_type.upper()}")
    print(f"  Quantity   : {quantity}")
    if price is not None:
        print(f"  Price      : {price}")
    if stop_price is not None:
        print(f"  Stop Price : {stop_price}")
    print("=" * 55 + "\n")


def print_order_response(response: dict):
    print("\n" + "=" * 55)
    print("         ORDER RESPONSE")
    print("=" * 55)
    print(f"  Order ID      : {response.get('orderId', 'N/A')}")
    print(f"  Symbol        : {response.get('symbol', 'N/A')}")
    print(f"  Side          : {response.get('side', 'N/A')}")
    print(f"  Type          : {response.get('type', 'N/A')}")
    print(f"  Status        : {response.get('status', 'N/A')}")
    print(f"  Executed Qty  : {response.get('executedQty', 'N/A')}")
    print(f"  Avg Price     : {response.get('avgPrice', 'N/A')}")
    print(f"  Time in Force : {response.get('timeInForce', 'N/A')}")
    print("=" * 55)
    print("\n  [SUCCESS]  Order placed successfully!\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    logger.info(
        "CLI invoked — symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        args.symbol, args.side, args.order_type, args.quantity,
        args.price, args.stop_price,
    )

    # 1. Validate input
    try:
        validate_order_params(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(f"\n  [FAILED]  Validation Error: {exc}\n")
        sys.exit(1)

    # 2. Show what we're about to send
    print_request_summary(
        args.symbol, args.side, args.order_type,
        args.quantity, args.price, args.stop_price,
    )

    # 3. Initialise client
    try:
        client = BinanceFuturesClient()
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        print(f"\n  [FAILED]  Configuration Error: {exc}\n")
        sys.exit(1)

    # 4. Place the order
    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except BinanceAPIError as exc:
        logger.error("Binance API error: code=%s msg=%s", exc.code, exc.message)
        print(f"\n  [FAILED]  Binance API Error (code {exc.code}): {exc.message}\n")
        sys.exit(1)
    except requests.exceptions.Timeout:
        logger.error("Network timeout while placing order.")
        print("\n  [FAILED]  Network Error: Request timed out. Check your connection.\n")
        sys.exit(1)
    except requests.exceptions.ConnectionError as exc:
        logger.error("Network connection error: %s", exc)
        print(f"\n  [FAILED]  Network Error: Could not connect to Binance testnet.\n  Details: {exc}\n")
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n  [FAILED]  Unexpected Error: {exc}\n")
        sys.exit(1)

    # 5. Print the result
    print_order_response(response)


if __name__ == "__main__":
    main()
