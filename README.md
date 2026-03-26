# NSE Alert → Telegram Webhook

Receives TradingView alerts and forwards them instantly to your Telegram.

## Files in this package

| File | Purpose |
|------|---------|
| `telegram_webhook.py` | Main Flask server |
| `requirements.txt` | Python dependencies |
| `Procfile` | Process command for Railway/Render |
| `railway.toml` | Railway-specific config (auto health check) |

---

## Deploy to Railway in 5 steps

1. **Create a free account** at https://railway.app

2. **Create a new project**
   - Click "New Project" → "Deploy from GitHub repo"
   - If you don't want to use GitHub: click "Deploy a template" → choose "Empty project" → then drag-and-drop these files using the Railway file upload

3. **Set environment variables**
   In your Railway project → Variables tab → add:
   ```
   BOT_TOKEN   =  your telegram bot token (from @BotFather)
   CHAT_ID     =  your chat id (from @userinfobot)
   ```

4. **Get your public URL**
   Railway → Settings → Networking → Generate Domain
   Your webhook URL will be:  `https://your-app-name.railway.app/webhook`

5. **Paste into TradingView**
   Create Alert → Notifications tab → tick "Webhook URL" → paste the URL above

---

## Get your Telegram credentials

### BOT_TOKEN
1. Open Telegram → search `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g. "NSE Alerts") and username (e.g. `nse_alerts_bot`)
4. BotFather replies with your token — looks like:  `7412356789:AAFxxxxxxxxxxxxxxxxxxxxxxx`

### CHAT_ID
1. Open Telegram → search `@userinfobot`
2. Send `/start`
3. It replies with your ID — looks like:  `987654321`

---

## Test it locally first (optional)

```bash
pip install flask requests gunicorn

# Set your credentials
export BOT_TOKEN="your_token_here"
export CHAT_ID="your_chat_id_here"

python telegram_webhook.py
```

Then in another terminal send a test alert:
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: text/plain" \
  -d "🟢 BUY @ 22450.5 | NSE:NIFTY | TF:5m | Test alert"
```

You should receive the message on Telegram within 1–2 seconds.

---

## TradingView alert message templates

Use these in the "Message" field when creating your alert:

**BUY alert:**
```
🟢 BUY @ {{close}} | {{ticker}} | TF:{{interval}}m | SL below signal bar | {{timenow}}
```

**SELL alert:**
```
🔴 SELL @ {{close}} | {{ticker}} | TF:{{interval}}m | SL above signal bar | {{timenow}}
```

**Any signal (combined):**
```
⚡ SIGNAL | {{ticker}} | Price:{{close}} | TF:{{interval}}m | {{timenow}}
```
