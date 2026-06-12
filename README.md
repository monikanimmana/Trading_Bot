# 🤖 Binance Futures Testnet Trading Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white)
![Binance](https://img.shields.io/badge/Binance-Futures_Testnet-F0B90B?style=for-the-badge&logo=binance&logoColor=white)
![REST API](https://img.shields.io/badge/REST-API-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**A clean, well-structured CLI trading bot that places real orders on the Binance USDT-M Futures Testnet.**  
Supports MARKET and LIMIT orders with full validation, structured logging, and graceful error handling.

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 📈 **Order Types** | MARKET and LIMIT orders |
| 🔄 **Sides** | BUY and SELL |
| 🔐 **Auth** | HMAC-SHA256 signed requests |
| ✅ **Validation** | Full input validation before any API call |
| 📋 **Logging** | Rotating file + console logs with timestamps |
| ⚠️ **Error Handling** | API errors, network failures, bad input — all handled |
| 🔑 **Secure** | API keys in `.env` — never hardcoded or committed |

---

## 📁 Project Structure

```
trading_bot/
├── 📂 bot/
│   ├── __init__.py          # Package marker
│   ├── client.py            # Binance API wrapper (auth, signing, HTTP)
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # CLI input validation
│   └── logging_config.py   # File + console logging setup
├── 📂 logs/                 # Log files written here at runtime
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # Template for API credentials
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Get Binance Futures Testnet API Keys

> 🆓 The testnet uses **fake money only** — no real funds involved.

1. Go to **[https://testnet.binancefuture.com](https://testnet.binancefuture.com)**
2. Click **Log In** → sign in with your **GitHub account**
3. Click your avatar (top right) → **API Key** → **Create**
4. Copy both the **API Key** and **Secret Key** shown

---

### 2. Clone & Install

```bash
git clone https://github.com/monikanimmana/Trading_Bot.git
cd Trading_Bot
```

```bash
# Create and activate virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

---

### 3. Configure API Keys

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> ⚠️ `.env` is listed in `.gitignore` — it will **never** be committed.

---

## 🚀 Usage

### CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair, e.g. `BTCUSDT` |
| `--side` | ✅ | `BUY` or `SELL` |
| `--type` | ✅ | `MARKET` or `LIMIT` |
| `--quantity` | ✅ | Contract quantity, e.g. `0.01` |
| `--price` | LIMIT only | Limit price, e.g. `120000` |

---

### 📟 Example Commands

**Market BUY**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Limit SELL**
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 120000
```

**Validation failure — missing `--price` for LIMIT**
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01
# ❌  Validation Error: --price is required for LIMIT orders.
```

---

## 🖥️ Sample Output

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
  Order ID      : 15014914737
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : NEW
  Executed Qty  : 0.0000
  Avg Price     : N/A
  Time in Force : GTC
=======================================================

  [SUCCESS]  Order placed successfully!
```

---

## 📋 Logs

Logs are written to `logs/trading_bot_YYYYMMDD.log` with rotating file handler (max 5 MB × 3 backups).

**Log format:**
```
2026-06-12 16:13:11 | INFO     | trading_bot.orders | Placing order — symbol=BTCUSDT side=BUY type=MARKET qty=0.01
2026-06-12 16:13:13 | INFO     | trading_bot.orders | Order accepted — orderId=15014914737 status=NEW
```

| Level | What's logged |
|---|---|
| `DEBUG` | Full request/response details (no secrets) |
| `INFO` | Key events — order placed, accepted |
| `ERROR` | Validation failures, API errors, network issues |

---

## 🏗️ Architecture

Each module has a **single responsibility** — no business logic leaks between layers.

```
cli.py  ──▶  validators.py  ──▶  orders.py  ──▶  client.py  ──▶  Binance Testnet
  │                                                                       │
  └──────────────────────── response / error ◀────────────────────────────
```

| Module | Responsibility |
|---|---|
| `client.py` | HMAC signing, HTTP transport, error mapping |
| `orders.py` | Builds order params, calls client, returns response |
| `validators.py` | Validates all user input before any API call |
| `logging_config.py` | One-time logging setup (file + console) |
| `cli.py` | Parses args → validates → places order → prints result |

---

## 🛡️ Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `--price` for LIMIT | Validation error, exits with code 1 |
| Invalid `--side` value | Validation error, exits with code 1 |
| Wrong symbol (e.g. `XXXXUSDT`) | Binance API error printed, exits with code 1 |
| Network timeout | Friendly timeout message, exits with code 1 |
| Missing API keys in `.env` | Configuration error printed, exits with code 1 |

---

## 📝 Assumptions

- Targets **USDT-M Futures Testnet** only (`https://testnet.binancefuture.com`)
- `timeInForce` is `GTC` (Good Till Cancel) for LIMIT orders
- Testnet credentials are separate from real Binance credentials

---

## 👩‍💻 Author

**Nimmana Monika**  
[![GitHub](https://img.shields.io/badge/GitHub-monikanimmana-181717?style=flat&logo=github)](https://github.com/monikanimmana)

---

<div align="center">
  <sub>Built for Binance Futures Testnet · Uses fake funds only · Safe to run</sub>
</div>
