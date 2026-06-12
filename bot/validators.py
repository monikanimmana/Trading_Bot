"""
Input validation for CLI arguments before any API call is made.
Raises ValueError with a human-readable message on invalid input.
"""

from typing import Optional
from .logging_config import get_logger

logger = get_logger("validators")

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # extendable


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> None:
    """
    Validate all order parameters.

    Raises:
        ValueError: with a descriptive message if any parameter is invalid.
    """
    logger.debug(
        "Validating params: symbol=%s side=%s type=%s qty=%s price=%s stop_price=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    # --- symbol ---
    if not symbol or not isinstance(symbol, str):
        raise ValueError("--symbol is required and must be a non-empty string.")
    symbol_clean = symbol.strip().upper()
    if len(symbol_clean) < 3:
        raise ValueError(f"Symbol '{symbol}' looks invalid. Example: BTCUSDT")

    # --- side ---
    if side.upper() not in VALID_SIDES:
        raise ValueError(
            f"--side must be one of {sorted(VALID_SIDES)}, got '{side}'."
        )

    # --- order type ---
    if order_type.upper() not in VALID_TYPES:
        raise ValueError(
            f"--type must be one of {sorted(VALID_TYPES)}, got '{order_type}'."
        )

    # --- quantity ---
    if quantity is None:
        raise ValueError("--quantity is required.")
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"--quantity must be a positive number, got '{quantity}'.")
    if qty <= 0:
        raise ValueError(f"--quantity must be greater than 0, got {qty}.")

    # --- price (required for LIMIT) ---
    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValueError(
                "--price is required for LIMIT orders. "
                "Example: --price 95000"
            )
        try:
            p = float(price)
        except (TypeError, ValueError):
            raise ValueError(f"--price must be a positive number, got '{price}'.")
        if p <= 0:
            raise ValueError(f"--price must be greater than 0, got {p}.")

    # --- stop_price (required for STOP_MARKET) ---
    if order_type.upper() == "STOP_MARKET":
        if stop_price is None:
            raise ValueError(
                "--stop-price is required for STOP_MARKET orders. "
                "Example: --stop-price 94000"
            )
        try:
            sp = float(stop_price)
        except (TypeError, ValueError):
            raise ValueError(
                f"--stop-price must be a positive number, got '{stop_price}'."
            )
        if sp <= 0:
            raise ValueError(f"--stop-price must be greater than 0, got {sp}.")

    logger.debug("Validation passed.")
