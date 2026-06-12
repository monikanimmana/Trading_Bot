# Binance Futures Testnet Trading Bot

A command-line Python trading bot that places **MARKET**, **LIMIT**, and **STOP_MARKET** orders on the Binance USDT-M Futures **Testnet**.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # package marker
│   ├── client.py            # Binance API wrapper (auth, signing, HTTP)
│   ├── orders.py            # order placement logic
│   ├── validators.py        # CLI input validation
│   └── logging_config.py   # file + console logging setup
├── cli.py                   # CLI entry point (argparse)
├── logs/                    # log files written here at runtime
├── .env.example             # template for API credentials
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 1 · Get Binance Futures Testnet API Keys

1. Open [https://testnet.binancefuture.com](https://testnet.binancefuture.com) in your browser.
2. Click **Log In** → use your GitHub account (no real money involved).
3. After login, click your avatar (top-right) → **API Key**.
4. Click **Create** and copy both the **API Key** and **Secret Key**.

> ⚠️ Testnet keys are completely separate from real Binance keys.

---

## 2 · Install Dependencies

```bash
# (Recommended) create and activate a virtual environment first
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## 3 · Configure API Keys

Copy the example env file and fill in your testnet credentials:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and replace the placeholder values:

```
BINANCE_API_KEY=<your_testnet_api_key>
BINANCE_API_SECRET=<your_testnet_api_secret>
```

> `.env` is listed in `.gitignore` — it will never be committed.

---

## 4 · Run the Bot

All commands are run from inside the `trading_bot/` directory.

### Market BUY
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit SELL
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 95000
```

### Stop-Market SELL (Bonus order type)
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 94000
```

### Graceful validation failure (missing --price for LIMIT)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01
# → ❌  Validation Error: --price is required for LIMIT orders.
```

---

## 5 · CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair, e.g. `BTCUSDT` |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET`, `LIMIT`, or `STOP_MARKET` |
| `--quantity` | ✅ | Contract quantity, e.g. `0.01` |
| `--price` | LIMIT only | Limit price, e.g. `95000` |
| `--stop-price` | STOP_MARKET only | Trigger price, e.g. `94000` |

---

## 6 · Example Terminal Output

```
=======================================================
         ORDER REQUEST SUMMARY
=======================================================
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.01
=======================================================

=======================================================
         ORDER RESPONSE
=======================================================
  Order ID      : 3942751823
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Executed Qty  : 0.01
  Avg Price     : 96825.40
  Time in Force : GTC
=======================================================

  ✅  Order placed successfully!
```

---

## 7 · Log Files

Logs are written to `logs/trading_bot_YYYYMMDD.log`.

Each line has the format:
```
2025-06-12 14:23:01 | INFO     | trading_bot.orders | Order accepted — orderId=3942751823 status=FILLED executedQty=0.01 avgPrice=96825.40
```

- **DEBUG** entries capture full request/response details (without secrets).
- **INFO** entries summarise key events.
- **ERROR** entries capture validation failures, API errors, and network issues.

---

## 8 · Architecture Notes

| Module | Responsibility |
|---|---|
| `client.py` | HMAC signing, HTTP transport, error mapping |
| `orders.py` | Builds order params, calls client, returns response |
| `validators.py` | Validates all user input before any API call |
| `logging_config.py` | One-time logging setup (file + console) |
| `cli.py` | Parses args → validates → places order → prints result |

No business logic lives in `cli.py`. No CLI code lives in `orders.py`.

---

## 9 · Assumptions

- The bot targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`).
- `timeInForce` is hardcoded to `GTC` for LIMIT orders (standard default).
- Quantity precision must match the symbol's rules on Binance; the testnet mirrors mainnet rules for BTCUSDT (min qty 0.001).
- Stop-limit orders are implemented as `STOP_MARKET` (market execution at trigger price) as a bonus order type.

---

## 10 · Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | Validation error, exits with code 1 |
| Invalid `--side` value | Validation error, exits with code 1 |
| Wrong symbol (e.g. XXXXUSDT) | Binance API error printed, exits with code 1 |
| Network timeout | Friendly timeout message, exits with code 1 |
| Missing API keys in `.env` | Configuration error printed, exits with code 1 |
