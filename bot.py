"""
Day Trading Alert Bot - GitHub / Render Ready Version
- Reads DISCORD_WEBHOOK_URL from environment variable (fixes weird page issue)
- Reads TICKERS from environment variable or defaults
- Includes all 4 beginner alerts + Drop from Open

Designed for Webull stocks, alerts to Discord.
"""

import os
import yfinance as yf
import time
import requests
import pandas as pd
from datetime import datetime

# --- CONFIG (reads from env vars on Render, falls back to defaults locally) ---
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
# Allow TICKERS env var like "AAPL,TSLA,SPY" for easy dashboard editing
tickers_env = os.getenv("TICKERS", "")
if tickers_env:
    TICKERS = [t.strip().upper() for t in tickers_env.split(",") if t.strip()]
else:
    TICKERS = ["AAPL", "TSLA", "NVDA", "SPY", "QQQ"]

CHECK_EVERY_SECONDS = int(os.getenv("CHECK_INTERVAL", "60"))
VOLUME_MULTIPLIER = float(os.getenv("VOL_MULTIPLIER", "2.0"))
FAST_MOVE_PCT = float(os.getenv("FAST_MOVE_PCT", "1.5"))
DROP_FROM_OPEN_PCT = float(os.getenv("DROP_PCT", "2.0"))

def send_discord(title, description, color=0x00ff00):
    if not DISCORD_WEBHOOK_URL:
        print(f"[NO WEBHOOK SET] Would send: {title} - {description}")
        return
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": f"{os.getenv('TICKERS', 'Bot')} • Paper trade first!"}
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]}, timeout=10)
        if resp.status_code not in (200, 204):
            print(f"Discord failed {resp.status_code}: {resp.text[:200]}")
        else:
            print(f"✓ Sent: {title}")
    except Exception as e:
        print(f"Discord error: {e}")

def check_ticker(ticker):
    df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
    if len(df) < 25:
        return
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df['Close']
    volume = df['Volume']
    
    df['VolAvg20'] = volume.rolling(20).mean()
    df['5min_pct'] = close.pct_change(5) * 100
    df['DayHigh'] = df['High'].cummax()
    df['DayLow'] = df['Low'].cummin()

    last = df.iloc[-1]
    first_open = float(df.iloc[0]['Open'])
    price = float(last['Close'])
    vol = float(last['Volume'])
    vol_avg = float(last['VolAvg20']) if pd.notna(last['VolAvg20']) else 0
    pct_5m = float(last['5min_pct']) if pd.notna(last['5min_pct']) else 0
    drop_from_open = ((price - first_open) / first_open * 100) if first_open else 0

    # 1. VOLUME SPIKE
    if vol_avg > 0 and vol > vol_avg * VOLUME_MULTIPLIER:
        send_discord(f"🔊 {ticker} VOLUME SPIKE", f"Price: **${price:.2f}**\nVolume **{vol/vol_avg:.1f}x** normal\nSomething is happening, check Webull.", 0xffa500)

    # 2. FAST MOVER
    if abs(pct_5m) >= FAST_MOVE_PCT:
        send_discord(f"{'📈' if pct_5m>0 else '📉'} {ticker} MOVING FAST {'UP 🚀' if pct_5m>0 else 'DOWN 📉'}",
                     f"Price: **${price:.2f}**\nMoved **{pct_5m:+.2f}%** in 5 min.", 0x00ff00 if pct_5m>0 else 0xff0000)

    # 3. DAY HIGH/LOW
    prev_high = df.iloc[:-1]['High'].max()
    prev_low = df.iloc[:-1]['Low'].min()
    if price > prev_high:
        send_discord(f"🔥 {ticker} NEW DAY HIGH!", f"**${price:.2f}** broke ${prev_high:.2f}", 0x00ffff)
    if price < prev_low:
        send_discord(f"⚠️ {ticker} NEW DAY LOW", f"**${price:.2f}** below ${prev_low:.2f}", 0xff0000)

    # 4. DROP FROM OPEN (your request)
    if drop_from_open <= -DROP_FROM_OPEN_PCT:
        send_discord(f"📉 {ticker} DIP FROM OPEN -{DROP_FROM_OPEN_PCT}%",
                     f"Open: ${first_open:.2f}\nNow: **${price:.2f}** ({drop_from_open:+.2f}%)\nPossible dip-buy watch.", 0x5865F2)

print(f"Bot starting... Watching {TICKERS}")
print(f"Webhook set: {'Yes' if DISCORD_WEBHOOK_URL else 'No - set DISCORD_WEBHOOK_URL env var'}")
if DISCORD_WEBHOOK_URL:
    send_discord("Bot Started ✅ - GitHub Version", f"Watching: {', '.join(TICKERS)}\nAlerts: Volume, Fast Move, Day High/Low, Drop {DROP_FROM_OPEN_PCT}% from Open", 0x5865F2)

while True:
    try:
        for ticker in TICKERS:
            try: check_ticker(ticker)
            except Exception as e: print(f"{ticker} check failed: {e}")
            time.sleep(1)
    except Exception as e:
        print(f"Loop error: {e}")
    time.sleep(CHECK_EVERY_SECONDS)
