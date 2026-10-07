# Day Trading Discord Alert Bot
Beginner-friendly stock alerts for Webull traders. Sends Discord notifications for volume spikes, fast moves, day highs/lows, and dips from open.

## Features
- 🔊 Volume Spike (2x normal)
- ⚡ Fast Mover (1.5% in 5min)
- 🔥 New Day High / Low Breakout
- 📉 Drop From Open (e.g. -2% dip)

## Setup for 24/7 Free Hosting on Render.com

### 1. Create GitHub Repo
1. Go to github.com/new
2. Name it `day-trade-alert-bot`
3. Upload all files from this folder (bot.py, requirements.txt, README.md)

### 2. Deploy on Render (Free)
1. Go to https://dashboard.render.com/ -> New + -> Background Worker
2. Connect your GitHub repo `day-trade-alert-bot`
3. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
4. Add Environment Variable:
   - Key: `DISCORD_WEBHOOK_URL`
   - Value: your Discord webhook URL (Discord Channel -> Settings -> Integrations -> Webhooks)
5. Add Environment Variable (optional):
   - Key: `TICKERS`
   - Value: `AAPL,TSLA,SPY,NVDA,QQQ`
6. Click Create. Done! It will run 24/7.

### 3. Local Run
```bash
pip install -r requirements.txt
# On Windows: set DISCORD_WEBHOOK_URL=https://discord.com/...
# On Mac/Linux: export DISCORD_WEBHOOK_URL=https://discord.com/...
python bot.py
```

## Config
Edit these at top of bot.py or use env vars:
- TICKERS
- CHECK_EVERY_SECONDS
- DROP_FROM_OPEN_PCT (default 2.0)

Paper trade first! This is for alerts only, not financial advice.
