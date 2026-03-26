"""
NSE Intraday Signal → Telegram Bot
====================================
Receives TradingView webhook alerts and forwards them to Telegram.
Includes a self-ping keep-alive so Render's free tier never sleeps.

SETUP:
  1. Get BOT_TOKEN from @BotFather on Telegram
  2. Get CHAT_ID from @userinfobot on Telegram
  3. Set both as environment variables on Render (+ RENDER_URL)
  4. Deploy → paste https://your-app.onrender.com/webhook into TradingView
"""

import os
import threading
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN   = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID     = os.environ.get("CHAT_ID",   "YOUR_CHAT_ID_HERE")
RENDER_URL  = os.environ.get("RENDER_URL", "")   # e.g. https://nse-alerts.onrender.com

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# ─── TELEGRAM SENDER ──────────────────────────────────────────
def send_telegram(message: str) -> bool:
    payload = {
        "chat_id":    CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }
    try:
        resp = requests.post(TELEGRAM_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[ERROR] Telegram send failed: {e}")
        return False


# ─── KEEP-ALIVE (pings /health every 10 min) ──────────────────
def keep_alive():
    """Prevents Render free tier from spinning down during market hours."""
    if not RENDER_URL:
        print("[KEEP-ALIVE] RENDER_URL not set — skipping self-ping")
        return
    while True:
        time.sleep(600)   # 10 minutes
        try:
            requests.get(f"{RENDER_URL}/health", timeout=10)
            print("[KEEP-ALIVE] Pinged /health")
        except Exception as e:
            print(f"[KEEP-ALIVE] Ping failed: {e}")


# Start keep-alive in background thread on startup
threading.Thread(target=keep_alive, daemon=True).start()


# ─── ROUTES ───────────────────────────────────────────────────
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return jsonify({"status": "ready", "detail": "Send a POST request with your alert"}), 200

    raw = request.get_data(as_text=True).strip()

    if not raw:
        return jsonify({"status": "error", "detail": "empty body"}), 400

    print(f"[ALERT] {raw}")

    if "BUY" in raw.upper():
        formatted = f"<b>BUY SIGNAL</b>\n<code>{raw}</code>"
    elif "SELL" in raw.upper():
        formatted = f"<b>SELL SIGNAL</b>\n<code>{raw}</code>"
    else:
        formatted = f"<b>SIGNAL</b>\n<code>{raw}</code>"

    ok = send_telegram(formatted)
    return (jsonify({"status": "ok"}), 200) if ok else (jsonify({"status": "error"}), 500)


@app.route("/")
def index():
    return jsonify({"status": "running", "service": "NSE Alerts Bot"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[INFO] Server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
