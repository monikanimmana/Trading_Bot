"""
Order placement logic for Binance USDT-M Futures Testnet.

This module is the only place that calls client.py methods.
It contains no CLI logic and no direct input validation.
"""

from typing import Any, Dict, Optional

from .client import BinanceFuturesClient
from .logging_config import get_logger

logger = get_logger("orders")

ORDER_ENDPOINT = "/fapi/v1/order"


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Build and send an order to the Binance Futures Testnet.

    Parameters
    ----------
    client      : authenticated BinanceFuturesClient instance
    symbol      : e.g. "BTCUSDT"
    side        : "BUY" or "SELL"
    order_type  : "MARKET", "LIMIT", or "STOP_MARKET"
    quantity    : contract quantity
    price       : limit price (required for LIMIT orders)
    stop_price  : trigger price (required for STOP_MARKET orders)

    Returns
    -------
    dict  parsed JSON response from Binance

    Raises
    ------
    BinanceAPIError        on Binance-level failures
    requests.RequestException on network failures
    """
    params: Dict[str, Any] = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": quantity,
    }

    if order_type.upper() == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"  # Good Till Cancel

    if order_type.upper() == "STOP_MARKET":
        params["stopPrice"] = stop_price

    logger.info(
        "Placing order — symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    response = client.post(ORDER_ENDPOINT, params)

    logger.info(
        "Order accepted — orderId=%s status=%s executedQty=%s avgPrice=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
        response.get("avgPrice"),
    )

    return response
