"""
Binance Futures Testnet API client.

Handles:
- HMAC-SHA256 request signing
- Sending signed POST/GET requests to the testnet
- Raising structured exceptions on HTTP/API errors
"""

import hashlib
import hmac
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from .logging_config import get_logger

load_dotenv()

logger = get_logger("client")

TESTNET_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    """Raised when Binance returns a non-2xx response or an error JSON body."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceFuturesClient:
    """
    Thin wrapper around the Binance USDT-M Futures Testnet REST API.

    Responsibilities:
    - Load API key / secret from environment variables
    - Sign requests with HMAC-SHA256
    - Send requests and return parsed JSON
    - Log requests and responses (without exposing secrets)
    """

    def __init__(self):
        self.api_key: str = os.environ.get("BINANCE_API_KEY", "")
        self._api_secret: str = os.environ.get("BINANCE_API_SECRET", "")

        if not self.api_key or not self._api_secret:
            raise EnvironmentError(
                "BINANCE_API_KEY and BINANCE_API_SECRET must be set "
                "in your .env file or environment."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.info("BinanceFuturesClient initialised (testnet).")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: Dict[str, Any]) -> str:
        """Return HMAC-SHA256 signature for the given params dict."""
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _build_signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        params["timestamp"] = self._timestamp()
        params["signature"] = self._sign(params)
        return params

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def post(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a signed POST request to *endpoint* with *params*.

        Returns the parsed JSON response dict.
        Raises BinanceAPIError on Binance-level errors.
        Raises requests.RequestException on network errors.
        """
        signed = self._build_signed_params(params)

        # Log the request WITHOUT the secret or signature value
        safe_params = {k: v for k, v in signed.items() if k not in ("signature",)}
        logger.debug("POST %s  params=%s", endpoint, safe_params)

        url = f"{TESTNET_BASE_URL}{endpoint}"
        try:
            response = self.session.post(
                url, data=signed, timeout=DEFAULT_TIMEOUT
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out: POST %s", endpoint)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error: %s", exc)
            raise

        self._handle_response(response)
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Send a signed GET request (used for account/position queries)."""
        if params is None:
            params = {}
        signed = self._build_signed_params(params)
        safe_params = {k: v for k, v in signed.items() if k not in ("signature",)}
        logger.debug("GET %s  params=%s", endpoint, safe_params)

        url = f"{TESTNET_BASE_URL}{endpoint}"
        try:
            response = self.session.get(
                url, params=signed, timeout=DEFAULT_TIMEOUT
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out: GET %s", endpoint)
            raise
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error: %s", exc)
            raise

        self._handle_response(response)
        return response.json()

    # ------------------------------------------------------------------
    # Response handling
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_response(response: requests.Response) -> None:
        """
        Check the HTTP response for errors.

        Logs the raw response body at DEBUG level and raises
        BinanceAPIError if Binance signals a failure.
        """
        logger.debug(
            "Response HTTP %s: %s", response.status_code, response.text[:500]
        )

        if response.status_code != 200:
            try:
                data = response.json()
                code = data.get("code", response.status_code)
                msg = data.get("msg", response.text)
            except Exception:
                code = response.status_code
                msg = response.text
            logger.error("Binance API error — code=%s msg=%s", code, msg)
            raise BinanceAPIError(code, msg)
